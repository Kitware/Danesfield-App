/*#############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
#############################################################################*/

<template>
  <div>
    <vc-viewer @ready="ready">
      <vc-primitive-tileset :url="url" @readyPromise="readyPromise" />
    </vc-viewer>
  </div>
</template>

<script>
import { mapState } from "vuex";
import { loadWorkingSetById, getTilesetFolderId } from "../utils/loadDataset";

import { API_URL } from "../constants";

export default {
  data() {
    return {
      cesiumInstance: null,
    };
  },
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
  methods: {
    ready(cesiumInstance) {
      this.cesiumInstance = cesiumInstance;
    },
    readyPromise(tileset) {
      const { Cesium, viewer } = this.cesiumInstance;
      viewer.zoomTo(
        tileset,
        new Cesium.HeadingPitchRange(
          0.0,
          -0.5,
          tileset.boundingSphere.radius * 2.0
        )
      );
    },
  },
};
</script>
