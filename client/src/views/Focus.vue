<template>
  <FullScreenViewport>
    <FocusWorkspace
      :workspaces="workspaces"
      :boundDatasets="boundDatasets"
      :datasetIdMetaMap="datasetIdMetaMap"
      :focusedWorkspace="focusedWorkspace"
      :listingDatasetIdAndWorkingSets="listingDatasetIdAndWorkingSets"
      :setFocusedWorkspaceKey="setFocusedWorkspaceKey"
      :addWorkspace="addWorkspace"
      :removeWorkspace="removeWorkspace"
      :changeWorkspaceType="changeWorkspaceType"
      :vtkBGColor="vtkBGColor"
      :changeVTKBGColor="changeVTKBGColor"
      ref="focusWorkspace"
      />
    <SidePanel
    :top="64"
    :floating='false'
    :expanded='sidePanelExpanded'
    :footer='false'>
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
      <template slot="toolbar">
        <v-toolbar flat>
          <v-btn icon class="hidden-xs-only" v-if="customVizDatasetId" @click="customVizDatasetId=null">
            <v-icon>arrow_back</v-icon>
          </v-btn>
          <v-toolbar-title>{{!customVizDatasetId?"Working Set":"Custom"}}</v-toolbar-title>
        </v-toolbar>
      </template>
      <div class="main">
        <transition name="slide-fade" mode="out-in">
          <div v-if="!customVizDatasetId" class="datasets-pane" key="datasets">
            <v-select
              :items="workingSets"
              :value="selectedWorkingSetId"
              @change="change"
              class="working-set-selector py-1 px-2"
              item-text="name"
              item-value='_id'
              label="Select"
              hide-details></v-select>
            <v-list dense class="datasets">
              <draggable v-model="listingDatasetIdAndWorkingSets" :options="{
                  draggable:'.dataset',
                  handle:'.dataset',
                  forceFallback:true,
                  fallbackOnBody: false
                }"
                @start="transitionName=''"
                @end="transitionName='fade-group'">
                <transition-group :name="transitionName" tag="div">
                  <v-list-group
                    v-for="datasetIdAndWorkingSet in listingDatasetIdAndWorkingSets"
                    :key="datasetIdAndWorkingSet.datasetId+datasetIdAndWorkingSet.workingSet._id"
                    v-if="datasets[datasetIdAndWorkingSet.datasetId]"
                    class="dataset hover-show-parent"
                    append-icon="">
                    <v-list-tile
                      slot="activator"
                      class="width-fix">
                      <v-list-tile-action @click.stop>
                        <template v-if="workspaceSupportsDataset(focusedWorkspace,datasets[datasetIdAndWorkingSet.datasetId])">
                          <v-btn flat icon key="add" v-if="focusedWorkspace.layers.map(layer=>layer.dataset).indexOf(datasets[datasetIdAndWorkingSet.datasetId])===-1" color="grey lighten-2" @click="visualize(datasets[datasetIdAndWorkingSet.datasetId],focusedWorkspace)">
                            <v-icon>fa-globe-americas</v-icon>
                          </v-btn>
                          <v-btn flat icon key="remove" v-else color="grey darken-2" @click="removeDatasetFromWorkspace({dataset:datasets[datasetIdAndWorkingSet.datasetId],workspace:focusedWorkspace})">
                            <v-icon>fa-globe-americas</v-icon>
                          </v-btn>
                        </template>
                        <v-icon v-else color="grey lighten-3">fa-ban</v-icon>
                      </v-list-tile-action>
                      <v-list-tile-action class="hover-show-child" @click.stop :class="{show:selectedDatasetIds[datasetIdAndWorkingSet.datasetId]}">
                        <v-checkbox
                          v-model="selectedDatasetIds[datasetIdAndWorkingSet.datasetId]"></v-checkbox>
                      </v-list-tile-action>
                      <v-list-tile-content>
                          <v-list-tile-title>
                            <v-tooltip top open-delay="1000">
                              <span slot="activator">{{datasets[datasetIdAndWorkingSet.datasetId].name}}</span>
                              {{datasets[datasetIdAndWorkingSet.datasetId].name}}
                            </v-tooltip>
                          </v-list-tile-title>
                          <v-list-tile-sub-title>{{ datasetIdAndWorkingSet.workingSet._id!==selectedWorkingSetId? datasetIdAndWorkingSet.workingSet.name:'' }}</v-list-tile-sub-title>
                      </v-list-tile-content>
                      <v-list-tile-action class="hover-show-child" @click.stop>
                        <v-menu>
                          <v-btn class="group-menu-button" slot="activator" flat icon color="grey darken-2">
                            <v-icon>more_vert</v-icon>
                          </v-btn>
                          <v-list>
                            <v-list-tile @click="customDatasetVisualization(datasets[datasetIdAndWorkingSet.datasetId])">
                              <v-list-tile-title>Custom</v-list-tile-title>
                            </v-list-tile>
                          </v-list>
                        </v-menu>
                      </v-list-tile-action>
                    </v-list-tile>
                    <v-list-tile>
                      <v-list-tile-content>
                        <v-list-tile-title>
                          <v-layout>
                            <v-flex>
                              Opacity
                            </v-flex>
                            <v-flex>
                              <v-slider class="opacity-slider pr-3"
                                hide-details
                                :min="0"
                                :max="1"
                                :step="0.01"
                                :disabled="!currentLayer(datasetIdAndWorkingSet.datasetId)"
                                :value="currentLayer(datasetIdAndWorkingSet.datasetId)?currentLayer(datasetIdAndWorkingSet.datasetId).opacity:1"
                                @input="setWorkspaceLayerOpacity({layer:currentLayer(datasetIdAndWorkingSet.datasetId),opacity:$event})"></v-slider>
                            </v-flex>
                            <v-flex>
                              {{(currentLayer(datasetIdAndWorkingSet.datasetId)?currentLayer(datasetIdAndWorkingSet.datasetId).opacity:1).toFixed(2)}}
                            </v-flex>
                          </v-layout>
                        </v-list-tile-title>
                      </v-list-tile-content>
                    </v-list-tile>
                  </v-list-group>
                </transition-group>
              </draggable>
            </v-list>
            <div v-if="childrenWorkingSets.length" class="results">
              <v-divider></v-divider>
              <v-subheader>Derived working sets</v-subheader>
              <v-list dense expand>
                <v-list-group
                  v-for="workingSet in childrenWorkingSets"
                  :key="workingSet._id">
                  <v-list-tile slot="activator" class="hover-show-parent">
                    <v-list-tile-action class="hover-show-child" @click.stop :class="{show:includedChildrenWorkingSets.indexOf(workingSet)!==-1}">
                      <v-tooltip top open-delay="500">
                        <v-checkbox
                          slot="activator"
                          :input-value="includedChildrenWorkingSets.indexOf(workingSet)!==-1"
                          @change="childrenWorkingSetChecked($event,workingSet)"></v-checkbox>
                        {{includedChildrenWorkingSets.indexOf(workingSet)===-1?'Include':'Exclude'}}
                      </v-tooltip>
                    </v-list-tile-action>
                    <v-list-tile-content>
                      <v-list-tile-title>
                        <v-tooltip top open-delay="1000">
                          <span slot="activator">{{workingSet.name}}</span>
                          {{workingSet.name}}
                        </v-tooltip>
                      </v-list-tile-title>
                    </v-list-tile-content>
                    <v-list-tile-action class="hover-show-child" @click.stop>
                      <v-menu>
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
                  </v-list-tile>
                  <v-list-tile
                    v-for="datasetId in workingSet.datasetIds"
                    v-if="datasetId in datasets"
                    :key="datasetId">
                    <v-list-tile-content>
                      <v-list-tile-title>
                        <v-tooltip top open-delay="1000">
                          <span slot="activator">{{datasets[datasetId].name}}</span>
                          {{datasets[datasetId].name}}
                        </v-tooltip>
                      </v-list-tile-title>
                    </v-list-tile-content>
                  </v-list-tile>
                </v-list-group>
              </v-list>
            </div>
          </div>
          <VectorCustomVizPane 
          v-if="customVizDatasetId"
          :dataset="datasets[customVizDatasetId]"
          :summary="datasetIdMetaMap[customVizDatasetId].summary"
          />
        </transition>
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
import { mapState, mapGetters, mapMutations, mapActions } from "vuex";
import findIndex from "lodash-es/findIndex";
import draggable from "vuedraggable";

import girder from "../girder";
import { loadDatasetById } from "../utils/loadDataset";
import loadDatasetData from "../utils/loadDatasetData";
import eventstream from "../utils/eventstream";
import FocusWorkspace from "./FocusWorkspace";
import VectorCustomVizPane from "../components/VectorCustomVizPane/VectorCustomVizPane";
import { summarize } from "../utils/geojsonUtil";
import { getDefaultGeojsonVizProperties } from "../utils/getDefaultGeojsonVizProperties";

export default {
  name: "Focus",
  components: {
    FocusWorkspace,
    VectorCustomVizPane,
    draggable
  },
  data() {
    return {
      datasets: {},
      datasetIdMetaMap: {},
      boundDatasets: null,
      listingDatasetIdAndWorkingSets: [],
      selectedDatasetIds: {},
      includedChildrenWorkingSets: [],
      processes: ["DSM"],
      transitionName: "fade-group",
      customVizDatasetId: null
    };
  },
  computed: {
    user() {
      return this.$girder.user;
    },
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
    childrenWorkingSets() {
      return this.workingSets.filter(
        workingSet =>
          workingSet.parentWorkingSetId === this.selectedWorkingSetId
      );
    },
    layers: {
      get() {
        return this.focusedWorkspace.layers;
      },
      set(layers) {
        this.setWorkspaceLayers({
          workspace: this.focusedWorkspace,
          layers
        });
      }
    },
    ...mapState([
      "sidePanelExpanded",
      "workingSets",
      "selectedWorkingSetId",
      "workspaces",
      "focusedWorkspaceKey",
      "vtkBGColor"
    ]),
    ...mapGetters(["focusedWorkspace"])
  },
  watch: {
    user(user) {
      if (!user) {
        this.$router.push("/login");
      }
    },
    selectedWorkingSetId(selectedWorkingSetId) {
      if (selectedWorkingSetId) {
        this.listingDatasetIdAndWorkingSets = [];
        this.selectedDatasetIds = {};
        this.removeAllDatasetsFromWorkspaces();
      }
      this.load();
    }
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
      return Promise.all([
        ...this.childrenWorkingSets.map(async workingSet => {
          var datasets = await loadDatasetById(workingSet.datasetIds);
          this.addDatasets(datasets);
        }),
        loadDatasetById(selectedWorkingSet.datasetIds).then(datasets => {
          this.addDatasets(datasets);
          this.boundDatasets = datasets;
          this.listingDatasetIdAndWorkingSets = datasets.map(dataset => ({
            datasetId: dataset._id,
            workingSet: selectedWorkingSet
          }));
        })
      ]);
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
        if (!dataset.meta || !dataset.meta.vizProperties) {
          dataset = {
            ...dataset,
            ...{ meta: { vizProperties: getDefaultGeojsonVizProperties() } }
          };
        }
        this.$set(this.datasets, dataset._id, dataset);
      }
    },
    childrenWorkingSetChecked(value, workingSet) {
      if (value) {
        // Add
        this.includedChildrenWorkingSets.push(workingSet);
        workingSet.datasetIds.forEach(datasetId => {
          // Add if the dataset is not already in current workingset
          if (
            findIndex(
              this.listingDatasetIdAndWorkingSets,
              datasetIdAndWorkingSet =>
                datasetIdAndWorkingSet.datasetId === datasetId
            ) === -1
          ) {
            this.listingDatasetIdAndWorkingSets.push({ datasetId, workingSet });
          }
        });
      } else {
        // Remove
        let index = this.includedChildrenWorkingSets.indexOf(workingSet);
        this.includedChildrenWorkingSets.splice(index, 1);
        workingSet.datasetIds.forEach(datasetId => {
          let index = findIndex(
            this.listingDatasetIdAndWorkingSets,
            datasetIdAndWorkingSet =>
              datasetIdAndWorkingSet.datasetId === datasetId &&
              datasetIdAndWorkingSet.workingSet._id === workingSet._id
          );
          if (index !== -1) {
            this.listingDatasetIdAndWorkingSets.splice(index, 1);
          }
        });
      }
    },
    currentLayer(datasetId) {
      var index = this.focusedWorkspace.layers
        .map(layer => layer.dataset)
        .indexOf(this.datasets[datasetId]);
      return this.focusedWorkspace.layers[index];
    },
    async visualize(dataset, workspace) {
      await this.getDatasetMeta(dataset);
      this.addDatasetToWorkspace({ dataset, workspace });
    },
    async customDatasetVisualization(dataset) {
      if (dataset.geometa.driver === "GeoJSON") {
        await this.getDatasetMeta(dataset);
      }
      this.customVizDatasetId = dataset._id;
    },
    async getDatasetMeta(dataset) {
      if (!(dataset._id in this.datasetIdMetaMap)) {
        if (dataset.geometa.driver === "GeoJSON") {
          var geojson = await loadDatasetData(dataset);
          var summary = summarize(geojson);
          this.$set(this.datasetIdMetaMap, dataset._id, { geojson, summary });
        }
      }
    },
    ...mapMutations([
      "addWorkspace",
      "removeWorkspace",
      "changeWorkspaceType",
      "setFocusedWorkspaceKey",
      "addDatasetToWorkspace",
      "setWorkspaceLayerOpacity",
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

  .datasets-pane {
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  .working-set-selector {
    flex: 0 0 auto;
  }
  .datasets {
    flex: 1;
    overflow-y: auto;

    .opacity-slider {
      margin-top: -4px;
    }
  }
}

.hover-show-child {
  display: none;

  &.show {
    display: flex;
  }
}

.hover-show-parent {
  &:hover {
    .hover-show-child {
      display: inherit;
    }
  }
}

.width-fix {
  width: 100%;
}

// Hide sortable fallback ghost element
.sortable-fallback {
  display: none;
}
</style>

<style lang="scss">
.datasets-pane {
  .datasets {
    .dataset {
      .v-list__tile {
        padding: 0 10px 0 12px;

        .v-list__tile__action {
          min-width: inherit;
          flex: 0 0 32px;
        }
      }

      // A fix that when v-list-group is not an immediate child of v-list its transition is not working correctly
      .expand-transition-leave-to {
        display: none !important;
      }

      .expand-transition-enter-to {
        height: auto !important;
      }
    }
  }

  .results {
    .v-list__tile {
      .v-list__tile__action {
        min-width: inherit;
        flex: 0 0 32px;
      }
    }

    .v-list__group__header {
      .v-list__tile {
        padding-right: 0;
      }
    }
    .v-list__group__header__append-icon {
      padding-left: 0;
    }
  }
}

.narrow-list-tile-action.v-list__tile__action {
  min-width: inherit;
  flex: 0 0 32px;
}
</style>
