<template>
  <FullScreenViewport>
    <WorkspaceContainer 
      :focused="focusedWorkspace"
      @update:focused="setFocusedWorkspaceKey($event)"
      :autoResize="true"
      :max="2"
      :flex-grow-first="5/4"
    >
      <Workspace
        v-for="(workspace, key) in workspaces"
        :key="key"
        :identifier="key"
        @split="addWorkspace(workspace)"
        @close="removeWorkspace(key)">
        <template slot="actions">
          <WorkspaceAction :disabled="workspace.type==='map'" @click="changeWorkspaceType({workspace,type:'map'})">Map</WorkspaceAction>
          <WorkspaceAction :disabled="workspace.type==='vtk'" @click="changeWorkspaceType({workspace,type:'vtk'})">VTK</WorkspaceAction>
        </template>
        <GeojsMapViewport v-if="workspace.type==='map'" key="geojs-map"
          class='map'
          :viewport='viewport'
      	  ref='geojsMapViewport'
        >
          <GeojsTileLayer
            url='https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png'
            attribution='© OpenStreetMap contributors, © CARTO'
            :zIndex='0'>
          </GeojsTileLayer>
          <template v-for="(dataset,i) in workspace.datasets">
            <GeojsGeojsonDatasetLayer
              v-if="dataset.geometa.driver==='GeoJSON'"
              :key="dataset._id"
              :dataset="dataset"
              :zIndex="i+1">
            </GeojsGeojsonDatasetLayer>
            <GeojsTileLayer
              v-if="dataset.geometa.driver==='GeoTIFF'"
              :key="dataset._id"
              :url='getTileURL(dataset)'
              :keepLower="false"
              :zIndex='i+1'>
            </GeojsTileLayer>
          </template>
        </GeojsMapViewport>
        <div v-if="workspace.type==='vtk'">
          <VTKViewport>
            <OBJActor v-for="(dataset,i) in workspace.datasets" :key=i :url="`http://localhost:8081/api/v1/item/${dataset._id}/download`" />
          </VTKViewport>
        </div>
      </Workspace>
    </WorkspaceContainer>

    <SidePanel
    :top='64'
    :toolbar='{title: "Datasets"}'
    :expanded='true'
    :footer='false'
    >
      <template slot="actions">
        <SidePanelAction v-for="action of actions" :key='action.name' :disabled='action.disabled'>
          <v-menu offset-y v-if="action.name==='process'">
            <v-icon slot="activator">{{action.icon}}</v-icon>
            <v-list>
              <v-list-tile v-for="process in processes" :key="process" @click="processClicked(process)">
                <v-list-tile-title>{{process}}</v-list-tile-title>
              </v-list-tile>
            </v-list>
          </v-menu>
        </SidePanelAction>
      </template>
      <v-container grid-list-xs px-2>
        <v-layout row wrap>
          <v-flex xs12>
            <v-select
              :items="workingSets"
              :value="selectedWorkingSetId"
              @change="change"
              item-text="name"
              item-value='_id'
              label="Select"
              hide-details
            ></v-select>
          </v-flex>
        </v-layout>
      </v-container>
      <v-list dense expand class="datasets">
        <transition-group name="fade-group" tag="div">
          <v-list-tile
          v-for="dataset in datasets"
          :key="dataset._id"
          class="dataset"
          @click="123"
          >
            <v-list-tile-action>
              <template v-if="workspaceSupportsDataset(focusedWorkspace,dataset)">
                <v-btn flat icon key="add" v-if="focusedWorkspace.datasets.indexOf(dataset)===-1" color="grey lighten-2" @click="addDatasetToWorkspace({dataset,workspace:focusedWorkspace})">
                  <v-icon>fa-globe-americas</v-icon>
                </v-btn>
                <v-btn flat icon key="remove" v-else color="grey darken-2" @click="removeDatasetFromWorkspace({dataset,workspace:focusedWorkspace})">
                  <v-icon>fa-globe-americas</v-icon>
                </v-btn>
              </template>
              <v-icon v-else color="grey lighten-3">fa-ban</v-icon>
            </v-list-tile-action>
            <v-list-tile-content>
                <v-list-tile-title v-text="dataset.name"></v-list-tile-title>
            </v-list-tile-content>
          </v-list-tile>
        </transition-group>
      </v-list>
    </SidePanel>
  </FullScreenViewport>
</template>

<style lang="scss" scoped>
.map {
  z-index: 0;
}
</style>

<script>
import { mapState, mapGetters, mapMutations } from "vuex";
import { geometryCollection, point } from "@turf/helpers";
import bbox from "@turf/bbox";
import bboxPolygon from "@turf/bbox-polygon";
import buffer from "@turf/buffer";
import distance from "@turf/distance";

import girder from "../girder";
import { loadDatasetById } from "../utils/loadDataset";
import loadDatasetData from "../utils/loadDatasetData";
import { API_URL } from "../constants";
import eventstream from "../utils/eventstream";
import WorkspaceContainer from "../components/Workspace/Container";
import Workspace from "../components/Workspace/Workspace";
import WorkspaceAction from "../components/Workspace/Action";
import GeojsGeojsonDatasetLayer from "../components/geojs/GeojsGeojsonDatasetLayer";
import VTKViewport from "../components/vtk/VTKViewport";
import OBJActor from "../components/vtk/OBJActor";

export default {
  name: "Focus",
  components: {
    WorkspaceContainer,
    Workspace,
    WorkspaceAction,
    GeojsGeojsonDatasetLayer,
    VTKViewport,
    OBJActor
  },
  data() {
    return {
      viewport: {
        center: [-100, 30],
        zoom: 4
      },
      datasets: [],
      selectedDatasetIds: {},
      drawing: false,
      editing: false,
      processes: ["DSM"],
      focused: null
    };
  },
  computed: {
    actions() {
      return [
        {
          name: "process",
          icon: "developer_board",
          disabled: !Object.values(this.selectedDatasetIds).filter(
            value => value
          ).length
        }
      ];
    },
    ...mapState([
      "workingSets",
      "selectedWorkingSetId",
      "workspaces",
      "focusedWorkspaceKey"
    ]),
    ...mapGetters(["focusedWorkspace"]),
    user() {
      return this.$girder.user;
    }
  },
  watch: {
    user(user) {
      if (!user) {
        this.$router.push("/login");
      }
    },
    selectedWorkingSetId(selectedWorkingSetId) {
      if (selectedWorkingSetId) {
        this.datasets = [];
        this.selectedDatasetIds = {};
        this.removeAllDatasetsFromWorkspaces();
      }
      this.load();
    }
  },
  created() {
    this.datasetDataMap = new WeakMap();
    this.$store.dispatch("loadWorkingSets").then(() => {
      if (this.selectedWorkingSetId) {
        this.load();
      }
    });

    eventstream.on("job_status", e => {
      console.log(e);
      if (e.data.status === 3) {
        this.load();
      }
    });
  },
  methods: {
    change(workingSetId) {
      this.$store.commit("setSelectWorkingSetId", workingSetId);
    },
    load() {
      var selectedWorkingSet = this.workingSets.filter(
        workingSet => workingSet._id === this.selectedWorkingSetId
      )[0];
      if (!selectedWorkingSet) {
        return;
      }
      loadDatasetById(selectedWorkingSet.datasetIds).then(datasets => {
        this.datasets = datasets;
        var geojsViewport = this.$refs.geojsMapViewport[0];
        if (!geojsViewport) {
          return;
        }
        var bboxOfAllDatasets = bbox(
          geometryCollection(datasets.map(dataset => dataset.geometa.bounds))
        );
        var dist = distance(
          point([bboxOfAllDatasets[0], bboxOfAllDatasets[1]]),
          point([bboxOfAllDatasets[2], bboxOfAllDatasets[3]])
        );
        var bufferedBbox = bbox(
          buffer(bboxPolygon(bboxOfAllDatasets), dist / 4)
        );

        var zoomAndCenter = geojsViewport.$geojsMap.zoomAndCenterFromBounds(
          {
            left: bufferedBbox[0],
            right: bufferedBbox[2],
            top: bufferedBbox[3],
            bottom: bufferedBbox[1]
          }
        );
        this.viewport.center = zoomAndCenter.center;
        this.viewport.zoom = zoomAndCenter.zoom;
      });
    },
    getTileURL(dataset) {
      var url = `${API_URL}/item/${
        dataset._id
      }/tiles/zxy/{z}/{x}/{y}?${encodeURI(
        "encoding=PNG&projection=EPSG:3857"
      )}`;
      return url;
    },
    processClicked(process) {
      var itemId = Object.entries(this.selectedDatasetIds).filter(
        ([itemId, selected]) => selected
      )[0][0];
      return girder.girder.post(`/processing/generate_dsm/?itemId=${itemId}`);
    },
    workspaceSupportsDataset(workspace, dataset) {
      if (workspace.type === "map") {
        if (["GeoTIFF", "GeoJSON"].indexOf(dataset.geometa.driver) !== -1) {
          return true;
        }
      } else if (workspace.type === "vtk") {
        if (["OBJ"].indexOf(dataset.geometa.driver) !== -1) {
          return true;
        }
      }
      return false;
    },
    ...mapMutations([
      "addWorkspace",
      "removeWorkspace",
      "changeWorkspaceType",
      "setFocusedWorkspaceKey",
      "addDatasetToWorkspace",
      "removeDatasetFromWorkspace",
      "removeAllDatasetsFromWorkspaces"
    ])
  }
};
</script>

<style lang="scss" scoped>
.map {
  z-index: 0;
}
</style>

<style lang="scss">
.datasets {
  .list__tile__action,
  .list__tile__avatar {
    min-width: 40px;
    padding: 0 9px;
  }
}
</style>
