<script>
import JSZip from "jszip";

import macro from "vtk.js/Sources/macro";

import HttpDataAccessHelper from "vtk.js/Sources/IO/Core/DataAccessHelper/HttpDataAccessHelper";
import vtkFullScreenRenderWindow from "vtk.js/Sources/Rendering/Misc/FullScreenRenderWindow";

import vtkOBJReader from "vtk.js/Sources/IO/Misc/OBJReader";
import vtkMTLReader from "vtk.js/Sources/IO/Misc/MTLReader";
import vtkMapper from "vtk.js/Sources/Rendering/Core/Mapper";
import vtkActor from "vtk.js/Sources/Rendering/Core/Actor";

export default {
  name: "OBJActor",
  components: {},
  inject: ["renderWindow", "renderer", "viewport"],
  data() {
    return {
      actor: null
    };
  },
  computed: {},
  props: ["url"],
  mounted() {
    HttpDataAccessHelper.fetchBinary(this.url, {
      progressCallback: progressEvent => {
        var progress = null;
        if (progressEvent.lengthComputable) {
          const percent = Math.floor(
            100 * progressEvent.loaded / progressEvent.total
          );
          progress = percent;
        } else {
          progress = macro.formatBytesToProperUnit(progressEvent.loaded);
        }
        this.viewport.$emit("progress", progress);
      }
    }).then(content => {
      this.viewport.$emit("progress", null);
      this.loadZipContent(content);
    });
  },
  methods: {
    loadZipContent(zipContent) {
      const fileContents = { obj: {}, mtl: {}, img: {} };
      const zip = new JSZip();
      zip.loadAsync(zipContent).then(() => {
        let workLoad = 0;

        var done = () => {
          if (workLoad !== 0) {
            return;
          }
          // Attach images to MTLs
          Object.keys(fileContents.mtl).forEach(mtlFilePath => {
            const mtlReader = fileContents.mtl[mtlFilePath];
            const basePath = mtlFilePath
              .split("/")
              .filter((v, i, a) => i < a.length - 1)
              .join("/");
            mtlReader.listImages().forEach(relPath => {
              const key = `${basePath}/${relPath}`;
              const imgSRC = fileContents.img[key];
              if (imgSRC) {
                mtlReader.setImageSrc(relPath, imgSRC);
              }
            });
          });

          // Create pipeline from obj
          Object.keys(fileContents.obj).forEach(objFilePath => {
            const mtlFilePath = objFilePath.replace(/\.obj$/, ".mtl");
            const objReader = fileContents.obj[objFilePath];
            const mtlReader = fileContents.mtl[mtlFilePath];

            const size = objReader.getNumberOfOutputPorts();
            for (let i = 0; i < size; i++) {
              const source = objReader.getOutputData(i);
              const mapper = vtkMapper.newInstance();
              const actor = vtkActor.newInstance();
              this.actor = actor;
              const name = source.get("name").name;

              actor.setMapper(mapper);
              mapper.setInputData(source);
              this.renderer.addActor(actor);

              if (mtlReader && name) {
                mtlReader.applyMaterialToActor(name, actor);
              }
            }
          });
          this.renderer.resetCamera();
          this.renderWindow.render();

          // Rerender with hopefully all the textures loaded
          setTimeout(this.renderWindow.render, 500);
        };

        zip.forEach((relativePath, zipEntry) => {
          if (relativePath.match(/\.obj$/i)) {
            workLoad++;
            zipEntry.async("string").then(txt => {
              const reader = vtkOBJReader.newInstance({ splitMode: "usemtl" });
              reader.parseAsText(txt);
              fileContents.obj[relativePath] = reader;
              workLoad--;
              done();
            });
          }
          if (relativePath.match(/\.mtl$/i)) {
            workLoad++;
            zipEntry.async("string").then(txt => {
              const reader = vtkMTLReader.newInstance();
              reader.parseAsText(txt);
              fileContents.mtl[relativePath] = reader;
              workLoad--;
              done();
            });
          }
          if (relativePath.match(/\.jpg$/i) || relativePath.match(/\.png$/i)) {
            workLoad++;
            zipEntry.async("base64").then(txt => {
              const ext = relativePath.slice(-3).toLowerCase();
              fileContents.img[
                relativePath
              ] = `data:image/${ext};base64,${txt}`;
              workLoad--;
              done();
            });
          }
        });
      });
    }
  },
  beforeDestroy() {
    this.renderer.removeActor(this.actor);
    this.renderer.resetCamera();
    this.renderWindow.render();
  },
  render() {
    return null;
  }
};
</script>
