<template>
  <FullScreenViewport>
    <GeojsMapViewport
      class='map'
      :viewport.sync='viewport'
    >
      <GeojsTileLayer
        url='https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png'
        attribution='© OpenStreetMap contributors, © CARTO'
        :zIndex='0'>
      </GeojsTileLayer>
      <GeojsTileLayer v-for="(dataset, i) in geotiffDatasets" :key="'tile'+i"
        :url='getTileURL(dataset)'
        :zIndex='1'>
      </GeojsTileLayer>
      <GeojsGeojsonLayer v-for="(dataset, i) in geojsonDatasets" :key='i'
        :geojson='datasetDataMap.get(dataset)'
        :zIndex='2'>
      </GeojsGeojsonLayer>
    </GeojsMapViewport>

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
                <v-list-tile avatar :key="dataset._id" @click="123">
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
import { loadDatasetById } from "../utils/loadDataset";
import loadDatasetData from "../utils/loadDatasetData";
import { API_URL } from "../constants";
import eventstream from "../utils/eventstream";
import rest from "girder/src/rest";

export default {
  name: "focus",
  components: {},
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
      processes: ["DSM"]
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
      return this.datasets.filter(dataset => dataset.meta.type === "geojson");
    },
    geotiffDatasets() {
      return this.datasets.filter(dataset => dataset.meta.type === "geotiff");
    },
    ...mapState(["workingSets", "selectedWorkingSetId"])
  },
  created() {
    this.datasetDataMap = new WeakMap();
    this.$store.dispatch("loadWorkingSets").then(() => {
      if (this.selectedWorkingSetId) {
        this.load();
      }
    });

    eventstream.on("job_status", e => {
      if (e.data.status === 3) {
        this.load();
      }
    });
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
  methods: {
    change(workingSetId) {
      this.$store.commit("selectWorkingSetId", workingSetId);
    },
    load() {
      var selectedWorkingSet = this.workingSets.filter(
        workingSet => workingSet._id === this.selectedWorkingSetId
      )[0];
      loadDatasetById(selectedWorkingSet.datasetIds).then(datasets => {
        return Promise.all(
          datasets
            .filter(dataset => dataset.meta.type === "geojson")
            .map(dataset => {
              return loadDatasetData(dataset).then(data => {
                this.datasetDataMap.set(dataset, data);
              });
            })
        ).then(() => {
          this.datasets = datasets;
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
      return rest.post(`/processing/${itemId}`);
    }
  }
};
</script>
