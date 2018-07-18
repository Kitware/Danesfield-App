<template>
  <FullScreenViewport>
    <WorkspaceContainer 
      :focused="focusedWorkspace"
      @update:focused="setFocusedWorkspaceKey($event)"
      :autoResize="true"
      :max="2"
    >
      <Workspace
        v-for="(workspace, key) in workspaces"
        :key="key"
        :identifier="key"
        @split="addWorkspace(workspace)"
        @close="removeWorkspace(key)"
        :states="[{name:'Map',value:'map',disabled:workspace.type==='map'},{name:'VTK',value:'vtk',disabled:workspace.type==='vtk'}]"
        @stateChange="changeWorkspaceType({workspace,type:$event})"
        >
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
          <VTKViewport v-if="workspace.type==='vtk'"
            :background="vtkBGColor">
            <OBJMultiItemActor
              v-for="dataset in workspace.datasets"
              v-if="dataset.geometa.driver==='OBJ'"
              :key="dataset._id"
              :item="dataset" />
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

    <SidePanel
    :top="64"
    :floating='false'
    :toolbar='{title: "Working Set"}'
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
      <div class="main">
        <v-select
          :items="workingSets"
          :value="selectedWorkingSetId"
          @change="change"
          class="working-set-selector py-1 px-2"
          item-text="name"
          item-value='_id'
          label="Select"
          hide-details></v-select>
        <v-list dense two-line class="datasets">
          <transition-group name="fade-group" tag="div">
            <v-list-tile
              v-for="datasetIdAndWorkingSet in shownDatasetIdAndWorkingSets"
              v-if="datasets[datasetIdAndWorkingSet.datasetId]"
              :key="datasetIdAndWorkingSet.datasetId"
              class="dataset"
              @click="123">
              <v-list-tile-content>
                  <v-list-tile-title v-text="datasets[datasetIdAndWorkingSet.datasetId].name"></v-list-tile-title>
                  <v-list-tile-sub-title>{{ datasetIdAndWorkingSet.workingSet._id!==selectedWorkingSetId? datasetIdAndWorkingSet.workingSet.name:'' }}</v-list-tile-sub-title>
              </v-list-tile-content>
              <v-list-tile-action>
                <template v-if="workspaceSupportsDataset(focusedWorkspace,datasets[datasetIdAndWorkingSet.datasetId])">
                  <v-btn flat icon key="add" v-if="focusedWorkspace.datasets.indexOf(datasets[datasetIdAndWorkingSet.datasetId])===-1" color="grey lighten-2" @click="addDatasetToWorkspace({dataset:datasets[datasetIdAndWorkingSet.datasetId],workspace:focusedWorkspace})">
                    <v-icon>fa-globe-americas</v-icon>
                  </v-btn>
                  <v-btn flat icon key="remove" v-else color="grey darken-2" @click="removeDatasetFromWorkspace({dataset:datasets[datasetIdAndWorkingSet.datasetId],workspace:focusedWorkspace})">
                    <v-icon>fa-globe-americas</v-icon>
                  </v-btn>
                </template>
                <v-icon v-else color="grey lighten-3">fa-ban</v-icon>
              </v-list-tile-action>
            </v-list-tile>
          </transition-group>
        </v-list>
        <div v-if="childrenWorkingSets.length" class="results">
          <v-subheader>Results</v-subheader>
          <v-list dense expand>
            <v-list-group
              v-for="workingSet in childrenWorkingSets"
              :key="workingSet._id">
              <v-list-tile slot="activator" class="hover-show-parent">
                <v-list-tile-content>
                  <v-list-tile-title>{{workingSet.name}}</v-list-tile-title>
                </v-list-tile-content>
                <v-list-tile-action class="hover-show-child" @click.stop>
                  <v-menu offset-y absolute :nudge-bottom="20" :nudge-left="20">
                    <v-btn slot="activator" flat icon color="grey darken-2">
                      <v-icon>more_vert</v-icon>
                    </v-btn>
                    <v-list>
                      <v-list-tile @click="change(workingSet._id)">
                        <v-list-tile-title>Focus</v-list-tile-title>
                      </v-list-tile>
                    </v-list>
                  </v-menu>
                </v-list-tile-action>
                <v-list-tile-action class="hover-show-child" @click.stop :class="{show:includedChildrenWorkingSets.indexOf(workingSet)!==-1}">
                  <v-tooltip top open-delay="500">
                    <v-checkbox
                      slot="activator"
                      :input-value="includedChildrenWorkingSets.indexOf(workingSet)!==-1"
                      @change="childrenWorkingSetChecked($event,workingSet)"></v-checkbox>
                    <span>{{includedChildrenWorkingSets.indexOf(workingSet)===-1?'Include the datasets':'Exclude the datasets'}}</span>
                  </v-tooltip>
                </v-list-tile-action>
              </v-list-tile>
              <v-list-tile
                v-for="datasetId in workingSet.datasetIds"
                v-if="datasetId in datasets"
                :key="datasetId">
                <v-list-tile-content>
                  <v-list-tile-title>{{datasets[datasetId].name}}</v-list-tile-title>
                </v-list-tile-content>
              </v-list-tile>
            </v-list-group>
          </v-list>
        </div>
      </div>
    </SidePanel>
  </FullScreenViewport>
</template>

<style lang="scss" scoped>
.map {
  z-index: 0;
}
</style>

<script>
import Vue from "vue";
import { mapState, mapGetters, mapMutations, mapActions } from "vuex";
import { geometryCollection, point } from "@turf/helpers";
import bbox from "@turf/bbox";
import bboxPolygon from "@turf/bbox-polygon";
import buffer from "@turf/buffer";
import distance from "@turf/distance";
import difference from "lodash-es/difference";
import findIndex from "lodash-es/findIndex";

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
import OBJMultiItemActor from "../components/vtk/OBJMultiItemActor";
import Palette from "../components/vtk/Palette";

export default {
  name: "Focus",
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
    return {
      viewport: {
        center: [-100, 30],
        zoom: 4
      },
      datasets: {},
      shownDatasetIdAndWorkingSets: [],
      selectedDatasetIds: {},
      includedChildrenWorkingSets: [],
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
      "focusedWorkspaceKey",
      "vtkBGColor"
    ]),
    ...mapGetters(["focusedWorkspace"]),
    user() {
      return this.$girder.user;
    },
    childrenWorkingSets() {
      return this.workingSets.filter(
        workingSet =>
          workingSet.parentWorkingSetId === this.selectedWorkingSetId
      );
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
        this.shownDatasetIdAndWorkingSets = [];
        this.selectedDatasetIds = {};
        this.removeAllDatasetsFromWorkspaces();
      }
      this.load();
    }
    // includedChildrenWorkingSets(workingSets, oldWorkingSets) {
    //   var added = difference(workingSets, oldWorkingSets);
    //   var removed = difference(oldWorkingSets, workingSets);
    //   added.forEach(workingSet => {
    //     workingSet.datasetIds.forEach(datasetId => {
    //       this.shownDatasetIdAndWorkingSets.push({ datasetId, workingSet });
    //     });
    //   });
    //   removed.forEach(workingSet => {
    //     workingSet.datasetIds.forEach(datasetId => {
    //       let index = findIndex(
    //         this.shownDatasetIdAndWorkingSets,
    //         datasetIdAndWorkingSet =>
    //           datasetIdAndWorkingSet.datasetId === datasetId
    //       );
    //       this.shownDatasetIdAndWorkingSets.splice(index, 1);
    //     });
    //   });
    // }
  },
  created() {
    this.load();

    eventstream.on("job_status", e => {
      if (e.data.status === 3) {
        this.load();
      }
    });
  },
  beforeRouteLeave(to, from, next) {
    this.resetWorkspace();
    next();
  },
  methods: {
    change(workingSetId) {
      this.$store.commit("setSelectWorkingSetId", workingSetId);
    },
    async load() {
      this.includedChildrenWorkingSets = [];
      await this.loadWorkingSets();
      if (!this.selectedWorkingSetId) {
        return;
      }
      var selectedWorkingSet = this.workingSets.filter(
        workingSet => workingSet._id === this.selectedWorkingSetId
      )[0];
      if (!selectedWorkingSet) {
        return;
      }
      var ps = this.childrenWorkingSets.map(async workingSet => {
        var datasets = await loadDatasetById(workingSet.datasetIds);
        this.addDatasets(datasets);
      });
      loadDatasetById(selectedWorkingSet.datasetIds).then(datasets => {
        this.addDatasets(datasets);
        this.shownDatasetIdAndWorkingSets = datasets.map(dataset => ({
          datasetId: dataset._id,
          workingSet: selectedWorkingSet
        }));
        var geojsViewport = this.$refs.geojsMapViewport
          ? this.$refs.geojsMapViewport[0]
          : null;
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

        var zoomAndCenter = geojsViewport.$geojsMap.zoomAndCenterFromBounds({
          left: bufferedBbox[0],
          right: bufferedBbox[2],
          top: bufferedBbox[3],
          bottom: bufferedBbox[1]
        });
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
    addDatasets(datasets) {
      for (let dataset of datasets) {
        Vue.set(this.datasets, dataset._id, dataset);
      }
    },
    childrenWorkingSetChecked(value, workingSet) {
      if (value) {
        this.includedChildrenWorkingSets.push(workingSet);
        workingSet.datasetIds.forEach(datasetId => {
          this.shownDatasetIdAndWorkingSets.push({ datasetId, workingSet });
        });
      } else {
        let index = this.includedChildrenWorkingSets.indexOf(workingSet);
        this.includedChildrenWorkingSets.splice(index, 1);
        workingSet.datasetIds.forEach(datasetId => {
          let index = findIndex(
            this.shownDatasetIdAndWorkingSets,
            datasetIdAndWorkingSet =>
              datasetIdAndWorkingSet.datasetId === datasetId
          );
          this.shownDatasetIdAndWorkingSets.splice(index, 1);
        });
      }
    },
    ...mapMutations([
      "addWorkspace",
      "removeWorkspace",
      "changeWorkspaceType",
      "setFocusedWorkspaceKey",
      "addDatasetToWorkspace",
      "removeDatasetFromWorkspace",
      "removeAllDatasetsFromWorkspaces",
      "resetWorkspace",
      "changeVTKBGColor"
    ]),
    ...mapActions(["loadWorkingSets"])
  }
};
</script>

<style lang="scss" scoped>
.map {
  z-index: 0;
}

.main {
  position: absolute;
  top: 64px;
  bottom: 0;
  right: 0;
  left: 0;
  display: flex;
  flex-direction: column;

  .working-set-selector {
    flex-grow: 0;
  }
  .datasets {
    flex: 1;
  }
}

.hover-show-parent {
  .hover-show-child {
    display: none;

    &.show {
      display: flex;
    }
  }

  &:hover {
    .hover-show-child {
      display: inherit;
    }
  }
}
</style>

<style lang="scss">
.datasets {
  .dataset {
    .v-list__tile {
      padding: 0 5px 0 12px;
    }
  }
  .v-list__tile__action,
  .v-list__tile__avatar {
    min-width: 40px;
    padding: 0 9px;
  }
}

.results {
  .v-list__tile {
    padding-right: 0;

    .v-list__tile__action:last-child {
      min-width: 40px;
    }
  }
  .v-list__group__header__append-icon {
    padding-left: 0;
  }
}
</style>
