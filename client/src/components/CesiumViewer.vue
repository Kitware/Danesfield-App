/*#############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
#############################################################################*/

<template>
  <div ref="container" id="cesiumContainer" />
</template>

<script>
import { mapState } from "vuex";
import { loadWorkingSetById, getTilesetFolderId } from "../utils/loadDataset";

import { API_URL } from "../constants";

export default {
  asyncComputed: {
    async url() {
      const { output_folder_id } = await loadWorkingSetById(
        this.selectedWorkingSetId
      );
      if (output_folder_id) {
        const tilesetFolderId = await getTilesetFolderId(output_folder_id);

        return `${API_URL}/resource/path/download/${tilesetFolderId}/tiler/tileset.json`;
      }
      return null;
    },
  },
  computed: {
    ...mapState({
      selectedWorkingSetId: "selectedWorkingSetId",
    }),
  },
  data() {
    return {
      debugShowBoundingVolume: false,
      debugShowGeometricError: false,
      debugShowRenderingStatistics: false,
    };
  },
  mounted() {
    this.initViewer(this.url);
  },
  watch: {
    url(newUrl) {
      this.initViewer(newUrl);
    },
  },
  methods: {
    initViewer(url) {
      // delete the old viewer
      this.$refs.container.innerHTML = null;

      const viewer = new Cesium.Viewer("cesiumContainer");
      const scene = new Cesium.Cesium3DTileset({
        url,
        debugShowBoundingVolume: this.debugShowBoundingVolume,
        debugShowGeometricError: this.debugShowGeometricError,
        debugShowRenderingStatistics: this.debugShowRenderingStatistics,
      });
      const tileset = viewer.scene.primitives.add(scene);
      viewer.zoomTo(tileset, new Cesium.HeadingPitchRange(0, -0.5, 0));
    },
  },
};
</script>

<style lang="scss" scoped>
.viewport {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}
</style>
