<template>
  <FullScreenViewport>
    <WorkspaceContainer 
      :focused.sync="focused"
      :autoResize="true"
      :max="2"
      :flex-grow-first="5/4"
    >
      <Workspace
        :key="workspace.id"
        :identifier="workspace.id"
        v-for="workspace in workspaces"
        @split="createNewView(workspace.type)"
        @close="close(workspace)">
        <template slot="actions">
          <WorkspaceAction @click="changeToMap(workspace)">Map</WorkspaceAction>
          <WorkspaceAction @click="changeToPointCloud(workspace)">Point Cloud</WorkspaceAction>
        </template>
        <GeojsMapViewport v-if="workspace.type==='map'" key="geojs-map"
          class='map'
          :viewport.sync='viewport'
      	  ref='geojsMapViewport'
        >
          <GeojsTileLayer
            url='https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png'
            attribution='© OpenStreetMap contributors, © CARTO'
            :zIndex='0'>
          </GeojsTileLayer>
          <GeojsTileLayer v-for="(dataset, i) in geotiffDatasets" :key="'tile'+i"
            :url='getTileURL(dataset)'
            :keepLower="false"
            :zIndex='1'>
          </GeojsTileLayer>
          <GeojsGeojsonLayer v-for="(dataset, i) in geojsonDatasets" :key='i'
            :geojson='datasetDataMap.get(dataset)'
            :zIndex='2'>
          </GeojsGeojsonLayer>
        </GeojsMapViewport>
        <div v-if="workspace.type==='pc'">
          {{focused}}
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
          <v-flex xs12>
            <v-list>
              <template v-for="(dataset, index) in datasets">
                <v-divider v-if='index!==0' :key="index"></v-divider>
                <v-list-tile avatar :key="dataset._id" @click="123" :title='dataset.name'>
                  <v-list-tile-action>
                    <v-checkbox v-model="selectedDatasetIds[dataset._id]"></v-checkbox>
                  </v-list-tile-action>
                  <v-list-tile-content>
                    <v-list-tile-title>{{dataset.name}}</v-list-tile-title>
                  </v-list-tile-content>
                </v-list-tile>
              </template>
            </v-list>
          </v-flex>
        </v-layout>
      </v-container>
    </SidePanel>
  </FullScreenViewport>
</template>

<style lang="scss" scoped>
.map {
  z-index: 0;
}
</style>

<script>
import { mapState } from "vuex";
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

export default {
  name: "Focus",
  components: {
    WorkspaceContainer,
    Workspace,
    WorkspaceAction
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
      focused: null,
      workspaces: [{ type: "map", id: 0 }]
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
    geojsons() {
      return this.datasets.map(dataset => {
        return this.datasetDataMap.get(dataset);
      });
    },
    geojsonDatasets() {
      return this.datasets.filter(
        dataset => dataset.geometa && dataset.geometa.driver === "GeoJSON"
      );
    },
    geotiffDatasets() {
      return this.datasets.filter(
        dataset => dataset.geometa && dataset.geometa.driver === "GeoTIFF"
      );
    },
    ...mapState(["workingSets", "selectedWorkingSetId"])
  },
  watch: {
    selectedWorkingSetId(selectedWorkingSetId) {
      if (selectedWorkingSetId) {
        this.datasets = [];
        this.selectedDatasetIds = {};
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
        return Promise.all(
          datasets
            .filter(
              dataset => dataset.geometa && dataset.geometa.driver === "GeoJSON"
            )
            .map(dataset => {
              return loadDatasetData(dataset).then(data => {
                this.datasetDataMap.set(dataset, data);
              });
            })
        ).then(() => {
          this.datasets = datasets;
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

          var zoomAndCenter = this.$refs.geojsMapViewport[0].$geojsMap.zoomAndCenterFromBounds(
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
    createNewView(type) {
      this.workspaces.push({
        type,
        id: Math.random()
          .toString(36)
          .substring(7)
      });
    },
    close(workspace) {
      var index = this.workspaces.indexOf(workspace);
      this.workspaces.splice(index, 1);
    },
    changeToMap(workspace) {
      workspace.type = "map";
    },
    changeToPointCloud(workspace) {
      workspace.type = "pc";
    }
  }
};
</script>
