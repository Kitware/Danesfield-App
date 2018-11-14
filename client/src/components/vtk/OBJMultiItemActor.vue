/*#############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
#############################################################################*/

<script>
import vtkOBJReader from "vtk.js/Sources/IO/Misc/OBJReader";
import vtkMTLReader from "vtk.js/Sources/IO/Misc/MTLReader";
import vtkMapper from "vtk.js/Sources/Rendering/Core/Mapper";
import vtkActor from "vtk.js/Sources/Rendering/Core/Actor";
import macro from "vtk.js/Sources/macro";

export default {
  name: "OBJMultiItemActor",
  components: {},
  inject: ["renderWindow", "renderer", "viewport", "cache"],
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
  props: {
    item: Object,
    texture: Boolean
  },
  async mounted() {
    this._destroyed = false;
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
    if (!this._destroyed) {
      return this.buildPipeline();
    }
  },
  watch: {
    texture() {
      this._destroyActors();
      this.buildPipeline(false);
    }
  },
  methods: {
    _fetchObjFileContent(item) {
      if (this.cache.has(item._id)) {
        return Promise.resolve(this.cache.get(item._id));
      }
      return this.$girder
        .get(`item/${item._id}/download`, {
          onDownloadProgress: event => {
            this.onProgress(event);
          },
          responseType: "text"
        })
        .then(({ data }) => {
          this.cache.set(item._id, data);
          return data;
        });
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
        if (this.cache.has(item._id)) {
          return Promise.resolve(this.cache.get(item._id));
        }
        return this.$girder
          .get(`item/${item._id}/download`, {
            onDownloadProgress: event => {
              this.onProgress(event);
            }
          })
          .then(({ data }) => {
            this.cache.set(item._id, data);
            return data;
          });
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
        if (this.cache.has(item._id)) {
          return Promise.resolve(this.cache.get(item._id));
        }
        return this.$girder
          .get(`item/${item._id}/download`, {
            onDownloadProgress: event => {
              this.onProgress(event);
            },
            responseType: "blob"
          })
          .then(({ data }) => {
            data = this.blobToBase64(data);
            this.cache.set(item._id, data);
            return data;
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
    async buildPipeline(resetCamera = true) {
      const data = this.actorData;

      var objReaders = this._readObjs(data.obj);
      var mtlReaders = this._readMtls(data.mtl);
      this._readImages(data.image);

      const mtlReaderByName = {};
      const imageLoaded = [];

      if (this.texture) {
        // Attach images to MTLs
        for (let mtlReader of mtlReaders) {
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
        if (this._destroyed) {
          return;
        }
      }

      // Create VTK pipeline
      for (let objReader of objReaders) {
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
          if (actor.getTextures()[0]) {
            actor.getTextures()[0].setInterpolate(false);
          }
          this.actors.push(actor);
        }
      }
      for (let actor of this.actors) {
        this.renderer.addActor(actor);
      }
      this.viewport.$emit("progressMessage", null);
      if (resetCamera) {
        this.renderer.resetCamera();
      }
      this.renderWindow.render();
    },
    _readObjs(data) {
      return Object.entries(data).map(([name, info]) => {
        const objReader = vtkOBJReader.newInstance({ splitMode: "usemtl" });
        objReader.parseAsText(info.content);
        return objReader;
      });
    },
    _readMtls(data) {
      return Object.entries(data).map(([name, info]) => {
        var mtlReader = vtkMTLReader.newInstance();
        mtlReader.parseAsText(info.content);
        return mtlReader;
      });
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

      if (!this._destroyed) {
        this.viewport.$emit(
          "progressMessage",
          `${this.item.name} ${macro.formatBytesToProperUnit(
            this.totalBytesLoaded + this.currentBytesLoaded
          )}`
        );
      }
    },
    _destroyActors() {
      for (let actor of this.actors) {
        this.renderer.removeActor(actor);
      }
      this.actors = [];
    }
  },
  beforeDestroy() {
    this._destroyActors();
    this.viewport.$emit("progressMessage", null);
    this.renderer.resetCamera();
    this.renderWindow.render();
    this._destroyed = true;
  },
  render() {
    return null;
  }
};
</script>
