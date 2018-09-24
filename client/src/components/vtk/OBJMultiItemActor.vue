<script>
import vtkOBJReader from "vtk.js/Sources/IO/Misc/OBJReader";
import vtkMTLReader from "vtk.js/Sources/IO/Misc/MTLReader";
import vtkMapper from "vtk.js/Sources/Rendering/Core/Mapper";
import vtkActor from "vtk.js/Sources/Rendering/Core/Actor";
import macro from "vtk.js/Sources/macro";

export default {
  name: "OBJMultiItemActor",
  components: {},
  inject: ["renderWindow", "renderer", "viewport"],
  data() {
    return {
      actors: [],
      // Storage for OBJ, MTL, and image resources
      actorData: { obj: {}, mtl: {}, image: {} },
      totalBytesLoaded: 0,
      currentBytesLoaded: 0
    };
  },
  computed: {},
  props: ["item"],
  async mounted() {
    const objContent = await this._fetchObjFileContent(this.item);
    let mtlFileNames = this._parseMtlFileNames(objContent);
    const folderId = this.item.folderId;
    let mtlItems = await this._fetchItemsInFolder(folderId, mtlFileNames);
    let mtlContent = await this._fetchMtlFileContent(mtlItems);
    let imageFileNames = this._parseImageFileNames(mtlContent);
    let imageItems = await this._fetchItemsInFolder(folderId, imageFileNames);
    let imageContent = await this._fetchImageFileContent(imageItems);

    this.addObjContent(this.item.name, objContent);
    mtlItems.forEach((mtlItem, index) => {
      this.addMtlContent(mtlItem.name, mtlContent[index]);
    });
    imageItems.forEach((imageItem, index) => {
      this.addImageContent(imageItem.name, imageContent[index]);
    });
    return this.buildPipeline();
  },
  methods: {
    _fetchObjFileContent(item) {
      return this.$girder
        .get(`item/${item._id}/download`, {
          onDownloadProgress: event => {
            this.onProgress(event);
          },
          responseType: "text"
        })
        .then(({ data }) => data);
    },
    _parseMtlFileNames(content) {
      const mtlFileNames = [];
      const re = /^mtllib\s+(.*)$/;
      content.split("\n").forEach(line => {
        const result = line.trim().match(re);
        if (result !== null && result.length > 1) {
          mtlFileNames.push(result[1]);
        }
      });
      return [...new Set(mtlFileNames)];
    },
    async _fetchItemsInFolder(folderId, fileNames) {
      const requests = fileNames.map(fileName => {
        return this.$girder
          .get("item", {
            params: {
              folderId: folderId,
              name: fileName
            }
          })
          .then(({ data }) => data);
      });
      const responses = await Promise.all(requests);
      return responses.map(resp => resp[0]).filter(item => item);
    },
    _fetchMtlFileContent(items) {
      const requests = items.map(item => {
        return this.$girder
          .get(`item/${item._id}/download`, {
            onDownloadProgress: event => {
              this.onProgress(event);
            }
          })
          .then(({ data }) => data);
      });

      return Promise.all(requests);
    },
    _parseImageFileNames(mtlContent) {
      const fileNames = [];
      const re = /^map_\w+\s+(.*)$/;
      mtlContent.forEach(content => {
        content.split("\n").forEach(line => {
          const result = line.trim().match(re);
          if (result !== null && result.length > 1) {
            fileNames.push(result[1]);
          }
        });
      });
      return [...new Set(fileNames)];
    },
    _fetchImageFileContent(items) {
      const requests = items.map(item => {
        return this.$girder
          .get(`item/${item._id}/download`, {
            onDownloadProgress: event => {
              this.onProgress(event);
            },
            responseType: "blob"
          })
          .then(({ data }) => {
            return this.blobToBase64(data);
          });
      });
      return Promise.all(requests);
    },
    addObjContent(name, content) {
      this.actorData.obj[name] = { content: content };
    },
    addMtlContent(name, content) {
      this.actorData.mtl[name] = { content: content };
    },
    addImageContent(name, content) {
      this.actorData.image[name] = { content: content };
    },
    async buildPipeline() {
      const data = this.actorData;

      this._readObjs(data.obj);
      this._readMtls(data.mtl);
      this._readImages(data.image);

      const mtlReaderByName = {};
      const imageLoaded = [];

      // Attach images to MTLs
      for (let info of Object.values(data.mtl)) {
        const mtlReader = info.reader;

        mtlReader.getMaterialNames().forEach(materialName => {
          mtlReaderByName[materialName] = mtlReader;

          const material = mtlReader.getMaterial(materialName);
          if (material && material.image) {
            const promise = new Promise((resolve, reject) => {
              material.image.addEventListener("load", () => resolve(), {
                once: true
              });
              material.image.addEventListener("error", () => resolve(), {
                once: true
              });
            });
            imageLoaded.push(promise);
          }
        });

        mtlReader.listImages().forEach(imageName => {
          const image = data.image[imageName];
          if (image && image.inline) {
            mtlReader.setImageSrc(imageName, image.inline);
          }
        });
      }

      // Wait for texture images to load. If rendering occurs before textures are loaded,
      // WebGL reports errors like:
      //     RENDER WARNING: there is no texture bound to the unit 0
      await Promise.all(imageLoaded);

      // Create VTK pipeline
      for (let info of Object.values(this.actorData.obj)) {
        const objReader = info.reader;
        const size = objReader.getNumberOfOutputPorts();
        for (let i = 0; i < size; i++) {
          const source = objReader.getOutputData(i);
          const mapper = vtkMapper.newInstance();
          const actor = vtkActor.newInstance();
          const name = source.get("name").name;
          const mtlReader = mtlReaderByName[name];

          actor.setMapper(mapper);
          mapper.setInputData(source);

          if (mtlReader && name) {
            mtlReader.applyMaterialToActor(name, actor);
          }
          actor.getTextures()[0].setInterpolate(false);
          this.actors.push(actor);
        }
      }
      for (let actor of this.actors) {
        this.renderer.addActor(actor);
      }
      this.viewport.$emit("progressMessage", null);
      this.renderer.resetCamera();
      this.renderWindow.render();
    },
    _readObjs(data) {
      for (let [name, info] of Object.entries(data)) {
        const objReader = vtkOBJReader.newInstance({ splitMode: "usemtl" });
        objReader.parseAsText(info.content);
        data[name].reader = objReader;
      }
    },
    _readMtls(data) {
      for (let [name, info] of Object.entries(data)) {
        const mtlReader = vtkMTLReader.newInstance();
        mtlReader.parseAsText(info.content);
        data[name].reader = mtlReader;
      }
    },
    _readImages(data) {
      for (let [name, info] of Object.entries(data)) {
        data[name].inline = info.content;
      }
    },
    blobToBase64(blob) {
      return new Promise((resolve, reject) => {
        var reader = new FileReader();
        reader.onload = function() {
          var dataUrl = reader.result;
          resolve(dataUrl);
        };
        reader.readAsDataURL(blob);
      });
    },
    onProgress(event) {
      if (event.lengthComputable) {
        if (event.loaded === event.total) {
          this.totalBytesLoaded += event.total;
          this.currentBytesLoaded = 0;
        } else {
          this.currentBytesLoaded = event.loaded;
        }
      } else {
        this.totalBytesLoaded = event.loaded;
      }

      this.viewport.$emit(
        "progressMessage",
        `${this.item.name} ${macro.formatBytesToProperUnit(
          this.totalBytesLoaded + this.currentBytesLoaded
        )}`
      );
    }
  },
  beforeDestroy() {
    for (let actor of this.actors) {
      this.renderer.removeActor(actor);
    }
    this.renderer.resetCamera();
    this.renderWindow.render();
  },
  render() {
    return null;
  }
};
</script>
