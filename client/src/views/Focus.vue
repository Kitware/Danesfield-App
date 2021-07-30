/*#############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
#############################################################################*/

<template>
  <div class="full-screen">
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
    class="side-panel"
    :top="64"
    :floating='false'
    :expanded='sidePanelExpanded'
    :footer='false'>
      <template slot="actions">
        <SidePanelAction
          @click.stop="processConfirmDialog = true"
          :disabled="!selectedWorkingSetId">
          <v-icon>developer_board</v-icon>
        </SidePanelAction>
      </template>
      <template slot="toolbar">
        <v-toolbar flat>
          <v-btn icon class="hidden-xs-only" v-if="customVizDatasetId" @click="returnFromCustomViz">
            <v-icon>arrow_back</v-icon>
          </v-btn>
          <v-toolbar-title v-if="!customVizDatasetId">Working Set</v-toolbar-title>
          <v-toolbar-title v-else class="body-1">{{datasets[customVizDatasetId].name}}</v-toolbar-title>
          <v-spacer></v-spacer>
          <v-menu
            v-if="!customVizDatasetId"
            offset-y>
            <v-btn
              slot="activator"
              icon
              :disabled="!selectedWorkingSetId">
              <v-icon>more_vert</v-icon>
            </v-btn>
            <v-list>
              <v-list-tile
                v-if="!focusedWorkspace.layers.length && focusedWorkspace.type==='vtk'"
                @click="addAllDatasetsToWorkspace(focusedWorkspace)">
                <v-list-tile-content>
                  Visualize all
                </v-list-tile-content>
              </v-list-tile>
              <v-list-tile
                v-if="focusedWorkspace.layers.length && focusedWorkspace.type==='vtk'"
                @click="removeAllDatasetsFromWorkspace(focusedWorkspace)">
                <v-list-tile-content>
                  Remove all
                </v-list-tile-content>
              </v-list-tile>
              <v-divider v-if="focusedWorkspace.type==='vtk'" />
              <v-list-tile
                @click="toggleHideUnsupportedDatasets()">
                <v-list-tile-content>
                  {{hideUnsupportedDatasetsOnFocus?'Show':'Hide'}} unsupported datasets
                </v-list-tile-content>
              </v-list-tile>
              <v-list-tile
                @click="datasetDetailDialog=true">
                <v-list-tile-content>Datasets detail</v-list-tile-content>
              </v-list-tile>
              <v-divider />
              <v-list-tile
                :disabled="!evaluationItems.length&&!childrenWorkingSetEvaluationItems.length"
                @click="downloadCombinedResult">
                <v-list-tile-content>
                  Download{{evaluationItems.length?' step':''}} evaluation datasets
                </v-list-tile-content>
              </v-list-tile>
            </v-list>
          </v-menu>
        </v-toolbar>
      </template>
      <div class="main">
        <transition name="slide-fade" mode="out-in">
          <div v-if="!customVizDatasetId" class="datasets-pane" key="datasets">
            <v-select
              :items="flattenedWorkingSets"
              :value="selectedWorkingSetId"
              @change="change"
              class="working-set-selector px-2"
              item-text="workingSet.name"
              item-value='workingSet._id'
              label="Select"
              hide-details>
              <template slot="item" slot-scope="{item:flattened}">
                <div
                  :style="{paddingLeft:Math.min(12*flattened.level,50)+'px'}"
                  >{{flattened.workingSet.name.split(': ').slice(-1)[0]}}</div>
              </template>
            </v-select>
            <v-list dense class="datasets" ref="datasetsContainer">
              <v-list-tile
                v-if="hideUnsupportedDatasetsOnFocus && listingDatasetIdAndWorkingSets.filter(({datasetId})=>datasets[datasetId]&&!supportWorkspaceType(datasets[datasetId])).length">
                <div style="text-align:center;width:100%;">Unsupported datasets are hidden</div>
              </v-list-tile>
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
                    v-if="datasets[datasetIdAndWorkingSet.datasetId] && (!hideUnsupportedDatasetsOnFocus || supportWorkspaceType(datasets[datasetIdAndWorkingSet.datasetId]))"
                    class="dataset hover-show-parent"
                    append-icon="">
                    <v-list-tile
                      slot="activator">
                      <v-list-tile-action @click.stop v-if="supportWorkspaceType(datasets[datasetIdAndWorkingSet.datasetId])">
                        <template v-if="supportWorkspaceType(datasets[datasetIdAndWorkingSet.datasetId])==focusedWorkspace.type">
                          <v-btn flat icon key="add" v-if="focusedWorkspace.layers.map(layer=>layer.dataset).indexOf(datasets[datasetIdAndWorkingSet.datasetId])===-1" color="grey lighten-2" @click="addDatasetToFocusedWorkspace(datasets[datasetIdAndWorkingSet.datasetId])">
                            <v-icon>fa-globe-americas</v-icon>
                          </v-btn>
                          <v-btn flat icon key="remove" v-else color="grey darken-2" @click="removeDatasetFromWorkspace({dataset:datasets[datasetIdAndWorkingSet.datasetId],workspace:focusedWorkspace})">
                            <v-icon>fa-globe-americas</v-icon>
                          </v-btn>
                        </template>
                        <v-icon v-else color="grey lighten-3">fa-ban</v-icon>
                      </v-list-tile-action>
                      <!-- <v-list-tile-action class="hover-show-child" @click.stop :class="{show:selectedDatasetIds[datasetIdAndWorkingSet.datasetId]}">
                        <v-checkbox
                          v-model="selectedDatasetIds[datasetIdAndWorkingSet.datasetId]"></v-checkbox>
                      </v-list-tile-action> -->
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
                        <v-menu absolute>
                          <v-btn class="group-menu-button" slot="activator" flat icon color="grey darken-2">
                            <v-icon>more_vert</v-icon>
                          </v-btn>
                          <v-list>
                            <v-list-tile
                              :disabled="!datasets[datasetIdAndWorkingSet.datasetId].geometa.bounds"
                              @click="boundDatasets=[datasets[datasetIdAndWorkingSet.datasetId]]">
                              <v-list-tile-title>Zoom to</v-list-tile-title>
                            </v-list-tile>
                            <v-list-tile
                              @click="customDatasetVisualization(datasets[datasetIdAndWorkingSet.datasetId])"
                              :disabled="focusedWorkspace.layers.map(layer=>layer.dataset).indexOf(datasets[datasetIdAndWorkingSet.datasetId])===-1">
                              <v-list-tile-title>Customize</v-list-tile-title>
                            </v-list-tile>
                            <v-divider />
                            <v-list-tile
                              :href="`${API_URL}/item/${datasetIdAndWorkingSet.datasetId}/download`"
                               target="_blank">
                              <v-list-tile-title>Download</v-list-tile-title>
                            </v-list-tile>
                          </v-list>
                        </v-menu>
                      </v-list-tile-action>
                    </v-list-tile>
                    <v-list-tile v-if="supportWorkspaceType(datasets[datasetIdAndWorkingSet.datasetId])">
                      <v-list-tile-content>
                        <v-list-tile-title>
                          <v-layout>
                            <v-flex>
                              Opacity
                            </v-flex>
                            <v-flex>
                              <v-slider class="opacity-slider pl-1 pr-3"
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
            <template v-if="childrenWorkingSets.length">
              <v-divider></v-divider>
              <v-subheader>Derived working sets</v-subheader>
              <v-list dense expand class="results">
                <v-list-group
                  class="hover-show-parent"
                  v-for="workingSet in childrenWorkingSets"
                  :key="workingSet._id">
                  <v-list-tile slot="activator">
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
                          <v-list-tile v-if="includedChildrenWorkingSets.indexOf(workingSet)===-1" @click="childrenWorkingSetChecked(true,workingSet)">
                            <v-list-tile-title>Include</v-list-tile-title>
                          </v-list-tile>
                          <v-list-tile v-else @click="childrenWorkingSetChecked(false,workingSet)">
                            <v-list-tile-title>Exclude</v-list-tile-title>
                          </v-list-tile>
                          <v-divider />
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
            </template>
          </div>
          <VectorCustomVizPane
            v-if="customVizDatasetId && datasets[customVizDatasetId].geometa.driver === 'GeoJSON'"
            :dataset="datasets[customVizDatasetId]"
            :summary="datasetIdMetaMap[customVizDatasetId].summary"
            :preserve.sync="preserveCustomViz"
            />
          <GeotiffCustomVizPane
            v-if="customVizDatasetId && datasets[customVizDatasetId].geometa.driver === 'GeoTIFF'"
            :dataset="datasets[customVizDatasetId]"
            :meta="datasetIdMetaMap[customVizDatasetId]"
            :preserve.sync="preserveCustomViz"
            :palettePickerExtras="palettePickerExtras"
            />
        </transition>
      </div>
    </SidePanel>
    <v-dialog
      v-model="datasetDetailDialog"
      scrollable
      max-width="80%">
      <v-card>
        <v-card-title class="">Datasets ({{listingDatasetIdAndWorkingSets.length}})</v-card-title>
        <v-card-text>
          <v-data-table
            :headers="[
              { text: 'Name', value: 'name' },
              { text: 'Size', value: 'size' }
            ]"
            :items="listingDatasetIdAndWorkingSets.map(item=>datasets[item.datasetId]).filter(dataset=>dataset)"
            hide-actions>
            <template slot="items" slot-scope="{item}">
              <tr @click="datasetDetailClicked(item)">
                <td>{{ item.name }}</td>
                <td>{{ item.size }}</td>
              </tr>
            </template>
          </v-data-table>
        </v-card-text>
      </v-card>
    </v-dialog>
    <v-dialog
      v-model="processConfirmDialog"
      max-width="400">
      <v-card class="start-processing">
        <v-card-title class="headline">Start a pipeline?</v-card-title>
        <v-card-text>
          A pipeline will be started with datasets within the current working set as input data. Multiple result working sets will be created.
          <div class="ml-1">
            <v-container grid-list-md class="pa-0">
              <v-layout>
                <v-flex>
                  <file-selector
                    label="Point Cloud File"
                    @file="setWorkflowPointCloudFile"
                    :value="workflowPointCloudFileName"
                    hide-details
                    dense
                  />
                </v-flex>
              </v-layout>
              <v-layout>
                <v-flex xs6>
                  <v-select
                    :items="[{name:'Standard',value:'STANDARD'},
                      {name:'D1',value:'D1'},
                      {name:'D2',value:'D2'},
                      {name:'D3',value:'D3'},
                      {name:'D4',value:'D4'}]"
                    item-text="name"
                    item-value="value"
                    hide-details
                    label="Model"
                    dense
                    v-model="materialClassificationModel" />
                </v-flex>
              </v-layout>
              <v-progress-linear
                v-if="workflowPointCloudUploadProgress || startPipelineInProgress"
                :value="workflowPointCloudUploadProgress"
                :indeterminate="startPipelineInProgress"
                height="4"
              />
            </v-container>
          </div>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            flat
            @click="processConfirmDialog = false">
            Cancel
          </v-btn>
          <v-btn
            color="primary"
            :disabled="startPipelineConfirmDisabled"
            @click="startPipeline()">
            Confirm
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <Logo />
  </div>
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
import bbox from "@turf/bbox";
import bboxPolygon from "@turf/bbox-polygon";
import center from "@turf/center";
import { featureCollection } from "@turf/helpers";
import VectorCustomVizPane from "resonantgeoview/src/components/VectorCustomVizPane/VectorCustomVizPane";
import { getDefaultGeojsonVizProperties } from "resonantgeoview/src/utils/getDefaultGeojsonVizProperties";
import GeotiffCustomVizPane from "resonantgeoview/src/components/GeotiffCustomVizPane";
import { summarize } from "resonantgeoview/src/utils/geojsonUtil";
import Upload from "@girder/components/src/utils/upload";

import girder from "../girder";
import { API_URL, GIRDER_URL } from "../constants";
import {
  loadDatasetByWorkingSetId,
  saveDatasetMetadata
} from "../utils/loadDataset";
import loadDatasetData from "../utils/loadDatasetData";
import FocusWorkspace from "./FocusWorkspace";
import getLargeImageMeta from "../utils/getLargeImageMeta";
import FeatureSelector from "../components/FeatureSelector";
import { palette } from "../utils/materialClassificationMapping";
import { blueRed, blueWhiteRed, blackWhite } from "../utils/extraPalettes";
import Logo from "../components/Logo";
import postDownload from "../utils/postDownload";
import isOBJItem from "../utils/isOBJItem";
import FileSelector from '../components/FileSelector.vue';

export default {
  name: "Focus",
  components: {
    FocusWorkspace,
    VectorCustomVizPane,
    GeotiffCustomVizPane,
    draggable,
    FeatureSelector,
    FileSelector,
    Logo
  },
  data() {
    return {
      datasets: {},
      datasetIdMetaMap: {},
      boundDatasets: null,
      listingDatasetIdAndWorkingSets: [],
      selectedDatasetIds: {},
      includedChildrenWorkingSets: [],
      processConfirmDialog: false,
      transitionName: "fade-group",
      customVizDatasetId: null,
      preserveCustomViz: false,
      AOIFeature: null,
      materialClassificationModel: "STANDARD",
      workflowPointCloudFile: null,
      workflowPointCloudUploadProgress: null,
      workflowPointCloudFileName: null,
      startPipelineInProgress: false,
      datasetDetailDialog: false,
      evaluationItems: [],
      childrenWorkingSetEvaluationItems: [],
      palettePickerExtras: {
        Custom: [blueRed, blueWhiteRed],
        "Material Classification": [palette]
      }
    };
  },
  computed: {
    startPipelineConfirmDisabled() {
      return !(this.workflowPointCloudFile || this.workflowPointCloudFileName)
    },
    portal() {
      return {
        name: "title",
        text: this.customVizDatasetId ? "Customize" : null
      };
    },
    API_URL() {
      return API_URL;
    },
    user() {
      return this.$girder.user;
    },
    selectedWorkingSet() {
      return this.workingSets.filter(
        workingSet => workingSet._id === this.selectedWorkingSetId
      )[0];
    },
    childrenWorkingSets() {
      if (!this.selectedWorkingSetId) {
        return [];
      }
      return this.workingSets
        .filter(
          workingSet =>
            workingSet.parentWorkingSetId === this.selectedWorkingSetId
        )
        .reverse();
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
    AOIBbox() {
      if (!this.AOIFeature) {
        return null;
      }
      return bbox(featureCollection(this.AOIFeature));
    },
    AOIDisplay() {
      return this.AOIBbox.map(coord => coord.toFixed(4)).join(", ");
    },
    ...mapState([
      "sidePanelExpanded",
      "workingSets",
      "selectedWorkingSetId",
      "workspaces",
      "focusedWorkspaceKey",
      "vtkBGColor",
      "hideUnsupportedDatasetsOnFocus"
    ]),
    ...mapGetters(["focusedWorkspace", "flattenedWorkingSets"])
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
        this.datasets = {};
        this.datasetIdMetaMap = {};
        this.removeAllDatasetsFromWorkspaces();
        this.loadWorkflowPointCloud()
      }
      this.load();
    }
  },
  created() {
    this.load();

    this.jobStatusHandler = e => {
      if (e.data.status === 3) {
        this.load();
      }
    };
    girder.girder.sse.$on("message:job_status", this.jobStatusHandler);
  },
  beforeDestroy() {
    girder.girder.sse.$off("message:job_status", this.jobStatusHandler);
  },
  beforeRouteLeave(to, from, next) {
    this.resetWorkspace();
    next();
  },
  methods: {
    async ensurePointCloudFolder() {
      const {data: collections} = await girder.girder.get('collection', { params: {text: 'core3d', sort: 'name'}})
      const core3dCollection = collections.find((coll) => coll.name === 'core3d');

      const {data: folder} = await girder.girder.post('folder', null, {
        params: {
          parentType: 'collection',
          parentId: core3dCollection._id,
          name:  `(${this.selectedWorkingSet.name}) Point Cloud`,
          reuseExisting: true,
          public: true,
        }
      });

      return folder;
    },

    // Load point cloud if it's been set
    async loadWorkflowPointCloud() {
      const pointCloudWorkingSet = this.workingSets.find(
        (ws) => ws.parentWorkingSetId
          && ws.parentWorkingSetId === this.selectedWorkingSet._id
          && ws.name === `${this.selectedWorkingSet.name}: generate-point-cloud`,
      );

      if (!(pointCloudWorkingSet && pointCloudWorkingSet.datasetIds)) {
        this.workflowPointCloudFileName = null;
        this.workflowPointCloudFile = null;
        this.workflowPointCloudUploadProgress = null;
        return;
      }

      const itemId = pointCloudWorkingSet.datasetIds[0];
      const { data: item } = await girder.girder.get(`item/${itemId}`)
      this.workflowPointCloudFileName = item.name;
    },
    setWorkflowPointCloudFile(file) {
      this.workflowPointCloudFile = file;
      this.workflowPointCloudFileName = file.name
    },
    change(workingSetId) {
      this.$store.commit("setSelectWorkingSetId", workingSetId);
    },
    async load() {
      this.includedChildrenWorkingSets = [];
      await this.loadWorkingSets();
      if (!this.selectedWorkingSet) {
        return;
      }
      return Promise.all([
        this.loadWorkflowPointCloud(),
        this.tryLoadFilterAOIFeatures().then(feature => {
          this.AOIFeature = feature;
        }),
        this.getEvaluationDatasets(this.selectedWorkingSet._id).then(
          ({ evaluationItems, childrenWorkingSetEvaluationItems }) => {
            this.evaluationItems = evaluationItems;
            this.childrenWorkingSetEvaluationItems = childrenWorkingSetEvaluationItems;
          }
        ),
        loadDatasetByWorkingSetId(this.selectedWorkingSet._id).then(
          datasets => {
            this.addDatasets(datasets);
            this.boundDatasets = Object.values(this.datasets);
            this.listingDatasetIdAndWorkingSets = datasets.map(dataset => ({
              datasetId: dataset._id,
              workingSet: this.selectedWorkingSet
            }));
          }
        ),
        ...this.childrenWorkingSets.map(async workingSet => {
          var datasets = await loadDatasetByWorkingSetId(workingSet._id);
          this.addDatasets(datasets);
        })
      ]);
    },
    clearAOI() {
      // A fix, otherwise v-text will try to focus on a removed element
      setTimeout(() => {
        this.AOIFeature = null;
      }, 0);
    },
    async startPipeline() {
      // Upload point cloud file first, if necessary
      if (this.workflowPointCloudFile !== null) {
        const folder = await this.ensurePointCloudFolder();
        const uploadManager = new Upload(this.workflowPointCloudFile, {
          '$rest': girder.girder,
          parent: folder,
          progress: (val) => {
            this.workflowPointCloudUploadProgress = (val.current/val.size)*100;
          },
        });

        const file = await uploadManager.start();
        await girder.girder.post('processing/setPointCloud', null, {
          params: {
            workingSet: this.selectedWorkingSetId,
            itemId: file.itemId,
          }
        });
      }

      this.startPipelineInProgress = true;
      await girder.girder.post(
        `/processing/process/?workingSet=${
          this.selectedWorkingSetId
        }`
      );
      this.processConfirmDialog = false
      this.startPipelineInProgress = false;
      this.workflowPointCloudUploadProgress = null;
    },
    supportWorkspaceType(dataset) {
      if (
        dataset.geometa &&
        dataset.geometa.driver &&
        ["GeoTIFF", "GeoJSON"].indexOf(dataset.geometa.driver) !== -1
      ) {
        return "map";
      }
      if (isOBJItem(dataset)) {
        return "vtk";
      }
    },
    addDatasets(datasets) {
      datasets
        .filter(dataset => !dataset.name.endsWith(".tar"))
        .map(dataset => {
          if (!dataset.geometa) {
            dataset.geometa = {};
          } else {
            switch (dataset.geometa.driver) {
              case "GeoJSON":
                if (!dataset.meta || !dataset.meta.vizProperties) {
                  dataset = {
                    ...dataset,
                    ...{
                      meta: { vizProperties: getDefaultGeojsonVizProperties() }
                    }
                  };
                }
                break;
              case "GeoTIFF":
                if (!dataset.meta) {
                  dataset.meta = {};
                }
                break;
            }
          }
          this.$set(this.datasets, dataset._id, dataset);
        });
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
        setTimeout(() => {
          this.$refs.datasetsContainer.$el.scrollTop = this.$refs.datasetsContainer.$el.scrollHeight;
        }, 0);
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
          // Remove from workspace if being visualized
          if (
            this.focusedWorkspace.layers
              .map(layer => layer.dataset)
              .indexOf(this.datasets[datasetId]) !== -1
          ) {
            this.removeDatasetFromWorkspace({
              dataset: this.datasets[datasetId],
              workspace: this.focusedWorkspace
            });
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
    async getDatasetMeta(dataset) {
      if (!(dataset._id in this.datasetIdMetaMap)) {
        switch (dataset.geometa.driver) {
          case "GeoJSON":
            var geojson = await loadDatasetData(dataset);
            var summary = summarize(geojson);
            this.$set(this.datasetIdMetaMap, dataset._id, { geojson, summary });
            break;
          case "GeoTIFF":
            var meta = await getLargeImageMeta(dataset);
            this.tryApplyDefaultVizProperties(dataset, meta);
            this.$set(this.datasetIdMetaMap, dataset._id, meta);
            break;
        }
      }
    },
    async addDatasetToFocusedWorkspace(dataset) {
      await this.getDatasetMeta(dataset);
      this.addDatasetToWorkspace({ dataset, workspace: this.focusedWorkspace });
    },
    async addAllDatasetsToWorkspace() {
      await this.listingDatasetIdAndWorkingSets
        .map(({ datasetId }) => this.datasets[datasetId])
        .filter(
          dataset =>
            dataset &&
            this.supportWorkspaceType(dataset) === this.focusedWorkspace.type
        )
        .map(dataset => this.addDatasetToFocusedWorkspace(dataset));
    },
    async customDatasetVisualization(dataset) {
      this.customVizDatasetId = dataset._id;
    },
    returnFromCustomViz() {
      var dataset = this.datasets[this.customVizDatasetId];
      this.customVizDatasetId = null;
      if (this.preserveCustomViz) {
        this.preserveCustomViz = false;
        saveDatasetMetadata(dataset);
      }
    },
    tryApplyDefaultVizProperties(dataset, meta) {
      var bandName = Object.keys(meta.bands)[0];
      var min = parseInt(meta.bands[bandName].min.toFixed(0));
      var max = parseInt(meta.bands[bandName].max.toFixed(0));
      if (dataset.meta && dataset.meta.vizProperties) {
        return;
      }
      var vizProperties = null;
      // *MTL.tif - discrete labels, you already have this color map.
      if (dataset.name.endsWith("MTL.tif")) {
        vizProperties = {
          band: bandName,
          palette: palette,
          range: [0, 11],
          type: "discrete"
        };
      } else if (
        // DSM.tif - continuous, fit range
        // *DTM.tif - continuous, fit range
        dataset.name.endsWith("DSM.tif") ||
        dataset.name.endsWith("DTM.tif")
      ) {
        vizProperties = {
          band: bandName,
          palette: blueWhiteRed,
          range: [min, max],
          type: "linear"
        };
        //TODO: *CLS.tif - discrete labels (2, 6, 17), pick a color for each.
      } else {
        if (Object.keys(meta.bands).length === 1) {
          vizProperties = {
            band: bandName,
            palette: blueWhiteRed,
            range: [min, max],
            type: "linear"
          };
        }
      }
      if (vizProperties) {
        dataset.meta = {
          ...dataset.meta,
          ...{ vizProperties }
        };
      }
    },
    async tryLoadFilterAOIFeatures() {
      if (this.selectedWorkingSet.filterId) {
        try {
          var { data: filter } = await girder.girder.get(
            `filter/${this.selectedWorkingSet.filterId}`
          );
          var features = filter.conditions
            .map(condition => condition.geojson)
            .filter(feature => feature);
          return features;
        } catch (ex) {}
      }
      return null;
    },
    datasetDetailClicked(dataset) {
      window.open(`${GIRDER_URL}#item/${dataset._id}`, "_blank");
    },
    async getEvaluationDatasets(workingSetId) {
      return (await this.$girder.get(
        `workingSet/${workingSetId}/evaluationItems`
      )).data;
    },
    async downloadCombinedResult() {
      var {
        evaluationItems,
        childrenWorkingSetEvaluationItems
      } = await this.getEvaluationDatasets(this.selectedWorkingSet._id);
      var items = evaluationItems.length
        ? evaluationItems
        : childrenWorkingSetEvaluationItems;
      postDownload(`${API_URL}/resource/download`, {
        resources: JSON.stringify({
          item: items.map(dataset => dataset._id)
        })
      });
    },
    ...mapMutations([
      "addWorkspace",
      "removeWorkspace",
      "changeWorkspaceType",
      "setFocusedWorkspaceKey",
      "addDatasetToWorkspace",
      "setWorkspaceLayerOpacity",
      "removeDatasetFromWorkspace",
      "removeAllDatasetsFromWorkspace",
      "removeAllDatasetsFromWorkspaces",
      "resetWorkspace",
      "changeVTKBGColor",
      "toggleHideUnsupportedDatasets"
    ]),
    ...mapActions(["loadWorkingSets"]),
    ...mapActions("prompt", ["prompt"])
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
    min-height: 0;
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

// Hide sortable fallback ghost element
.sortable-fallback {
  display: none;
}
</style>

<style lang="scss">
.side-panel {
  .v-toolbar__title:not(:first-child) {
    margin-left: 0;
  }
}

.datasets-pane {
  .datasets {
    .v-list__group__header {
      > div:first-child {
        width: 100%;
      }

      .v-list__tile {
        padding: 0 10px 0 12px;

        .v-list__tile__action {
          min-width: inherit;
          flex: 0 0 32px;
        }
      }
    }

    .dataset {
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
    max-height: 50%;
    flex: 0 0 auto;
    overflow-y: auto;

    .v-list__tile {
      .v-list__tile__action {
        min-width: inherit;
        flex: 0 0 32px;
      }
    }

    .v-list__group__header {
      > div:first-child {
        width: calc(100% - 40px);
      }

      .v-list__tile {
        padding-right: 2px;
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

.logo {
  left: 3px;
  bottom: 43px;
}
</style>
