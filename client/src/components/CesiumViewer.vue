/*#############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
#############################################################################*/

<template>
  <div :style="{ height: '87%' }">
    <v-switch
      label="Show Bounding Volumes"
      v-model="debugShowBoundingVolume"
    ></v-switch>
    <vc-viewer baseLayerPicker fullscreenButton @ready="ready">
      <vc-layer-imagery>
        <vc-provider-imagery-ion :assetId="3" />
      </vc-layer-imagery>
      <vc-layer-imagery>
        <vc-provider-terrain-cesium />
      </vc-layer-imagery>
      <vc-primitive-tileset
        :url="url"
        @readyPromise="readyPromise"
        :debugShowContentBoundingVolume="debugShowBoundingVolume"
      />
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
      debugShowBoundingVolume: false,
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
