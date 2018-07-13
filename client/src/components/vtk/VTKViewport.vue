<template>
<div>
    <div class="vtk-viewport" ref="container">
        <div class="progressMessage" v-if='progressMessage'>{{progressMessage}}</div>
        <slot v-if="ready"></slot>
    </div>
    <div v-if="!$slots.default" class="no-actor"></div>
</div>
</template>

<script>
import vtkFullScreenRenderWindow from "vtk.js/Sources/Rendering/Misc/FullScreenRenderWindow";

export default {
  name: "VTKViewport",
  components: {},
  data() {
    return {
      renderWindow: null,
      renderer: null,
      ready: false,
      progressMessage: null
    };
  },
  computed: {},
  provide() {
    var provide = {
      viewport: this
    };
    Object.defineProperty(provide, "renderer", {
      get: () => this.renderer
    });
    Object.defineProperty(provide, "renderWindow", {
      get: () => this.renderWindow
    });
    return provide;
  },
  created() {
    this.$on("progressMessage", progressMessage => {
      this.progressMessage = progressMessage;
    });
  },
  mounted() {
    console.log("VTKViewport mounted");
    const fullScreenRenderer = vtkFullScreenRenderWindow.newInstance({
      background: [0.44, 0.44, 0.44],
      rootContainer: this.$refs.container,
      containerStyle: { height: "100%", width: "100%", position: "absolute" }
    });
    this.renderer = fullScreenRenderer.getRenderer();
    this.renderWindow = fullScreenRenderer.getRenderWindow();
    this.ready = true;
  },
  methods: {}
};
</script>

<style lang="scss" scoped>
.progressMessage {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 1;
  text-shadow: 0px 0px 6px rgba(0, 0, 0, 1);
  font-size: 20px;
  color: white;
  user-select: none;
}

.no-actor {
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  right: 0;
  background: #bdbdbd;

  &::after {
    content: "Add actors";
    position: absolute;
    top: 50%;
    left: 50%;
    font-size: 16px;
    transform: translate(-50%, -50%);
  }
}
</style>
