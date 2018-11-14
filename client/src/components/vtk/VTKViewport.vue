/*#############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
#############################################################################*/

<template>
<div class="vtk-viewport" ref="container" :style="{background}">
  <div class="progressMessage" v-if='progressMessage'>{{progressMessage}}</div>
  <slot v-if="ready"></slot>
  <div v-if="!$slots.default" class="no-actor"></div>
</div>
</template>

<script>
import vtkFullScreenRenderWindow from "vtk.js/Sources/Rendering/Misc/FullScreenRenderWindow";

export default {
  name: "VTKViewport",
  components: {},
  props: {
    background: {
      type: String,
      default: "#bdbdbd"
    }
  },
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
      viewport: this,
      cache: new Map()
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
    const fullScreenRenderer = vtkFullScreenRenderWindow.newInstance({
      background: [0, 0, 0, 0],
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
.vtk-viewport {
  height: 100%;
}

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
  background: white;

  &::after {
    content: "Add data";
    position: absolute;
    top: 50%;
    left: 50%;
    font-size: 16px;
    transform: translate(-50%, -50%);
  }
}
</style>
