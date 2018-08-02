<template>
<WorkspaceContainer 
  :focused="focusedWorkspace"
  @update:focused="setFocusedWorkspaceKey($event)"
  :autoResize="true"
  :max="2">
  <Workspace
    v-for="(workspace, key) in workspaces"
    :key="key"
    :identifier="key"
    @split="addWorkspace(workspace)"
    @close="removeWorkspace(key)"
    :states="[{name:'Map',value:'map',disabled:workspace.type==='map'},{name:'3D View',value:'vtk',disabled:workspace.type==='vtk'}]"
    @stateChange="changeWorkspaceType({workspace,type:$event})"
    >
    <GeojsMapViewport v-if="workspace.type==='map'" key="geojs-map"
      class='map'
      :viewport='viewport'
      ref='geojsMapViewport'>
      <GeojsTileLayer
        url='https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png'
        attribution='© OpenStreetMap contributors, © CARTO'
        :zIndex='0'>
      </GeojsTileLayer>
      <template v-for="(layer,i) in orderLayer(workspace.layers)">
        <GeojsGeojsonDatasetLayer
          v-if="layer.dataset.geometa.driver==='GeoJSON'"
          :key="layer.dataset._id"
          :dataset="layer.dataset"
          :opacity="layer.opacity"
          :zIndex="i+1">
        </GeojsGeojsonDatasetLayer>
        <GeojsTileLayer
          v-if="layer.dataset.geometa.driver==='GeoTIFF'"
          :key="layer.dataset._id"
          :url="getTileURL(layer.dataset)"
          :opacity="layer.opacity"
          :keepLower="false"
          :zIndex="i+1">
        </GeojsTileLayer>
      </template>
    </GeojsMapViewport>
      <VTKViewport v-if="workspace.type==='vtk'"
        :background="vtkBGColor">
        <OBJMultiItemActor
          v-for="layer in workspace.layers"
          v-if="layer.dataset.geometa.driver==='OBJ'"
          :key="layer.dataset._id"
          :item="layer.dataset" />
      </VTKViewport>
    <template slot='actions' v-if="workspace.type==='vtk'">
      <WorkspaceAction>
        <v-menu
          top offset-y
          origin="center center">
          <v-icon
            slot="activator"
          >palette</v-icon>
          <v-card width="130px">
            <Palette :value="vtkBGColor" @input="changeVTKBGColor($event)" />
          </v-card>
        </v-menu>
      </WorkspaceAction>
    </template>
  </Workspace>
</WorkspaceContainer>
</template>

<script>
import { geometryCollection, point } from "@turf/helpers";
import bbox from "@turf/bbox";
import bboxPolygon from "@turf/bbox-polygon";
import buffer from "@turf/buffer";
import distance from "@turf/distance";
import sortBy from "lodash-es/sortBy";

import { API_URL } from "../constants";
import WorkspaceContainer from "../components/Workspace/Container";
import Workspace from "../components/Workspace/Workspace";
import WorkspaceAction from "../components/Workspace/Action";
import GeojsGeojsonDatasetLayer from "../components/geojs/GeojsGeojsonDatasetLayer";
import VTKViewport from "../components/vtk/VTKViewport";
import OBJMultiItemActor from "../components/vtk/OBJMultiItemActor";
import Palette from "../components/vtk/Palette";

export default {
  name: "FocusWorkspaces",
  components: {
    WorkspaceContainer,
    Workspace,
    WorkspaceAction,
    GeojsGeojsonDatasetLayer,
    VTKViewport,
    OBJMultiItemActor,
    Palette
  },
  data() {
    return {};
  },
  computed: {
    viewport() {
      if (!this.boundDatasets) {
        return {
          viewport: {
            center: [-100, 30],
            zoom: 4
          }
        };
      } else {
        var geojsViewport = this.$refs.geojsMapViewport
          ? this.$refs.geojsMapViewport[0]
          : null;
        if (!geojsViewport) {
          return;
        }
        var bboxOfAllDatasets = bbox(
          geometryCollection(
            this.boundDatasets.map(dataset => dataset.geometa.bounds)
          )
        );
        var dist = distance(
          point([bboxOfAllDatasets[0], bboxOfAllDatasets[1]]),
          point([bboxOfAllDatasets[2], bboxOfAllDatasets[3]])
        );
        var bufferedBbox = bbox(
          buffer(bboxPolygon(bboxOfAllDatasets), dist / 4)
        );

        return geojsViewport.$geojsMap.zoomAndCenterFromBounds({
          left: bufferedBbox[0],
          right: bufferedBbox[2],
          top: bufferedBbox[3],
          bottom: bufferedBbox[1]
        });
      }
    }
  },
  props: [
    "boundDatasets",
    "workspaces",
    "listingDatasetIdAndWorkingSets",
    "focusedWorkspace",
    "setFocusedWorkspaceKey",
    "addWorkspace",
    "removeWorkspace",
    "changeWorkspaceType",
    "vtkBGColor",
    "changeVTKBGColor"
  ],
  methods: {
    getTileURL(dataset) {
      var url = `${API_URL}/item/${
        dataset._id
      }/tiles/zxy/{z}/{x}/{y}?${encodeURI(
        "encoding=PNG&projection=EPSG:3857"
      )}`;
      return url;
    },
    orderLayer(layers) {
      var orderedDatasetIds = this.listingDatasetIdAndWorkingSets.map(
        datasetIdAndWorkingSet => datasetIdAndWorkingSet.datasetId
      );
      return sortBy(layers, layer => {
        return -orderedDatasetIds.indexOf(layer.dataset._id);
      });
    }
  }
};
</script>

<style lang="scss" scoped>
</style>