/*#############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
#############################################################################*/

<template>
  <div class='edit-workingset'>
    <div class="mx-2">
      <v-text-field
        class="input"
        name="Name"
        label="Name"
        hint="A unique name for the working set"
        v-model="name">
      </v-text-field>
    </div>
    <div class='body-2 mx-2' v-if="datasets.length">Datasets</div>
    <transition name='fade'>
      <SlideFadeGroup class="datasets mx-2" tag='div'>
        <div v-for="dataset in filteredDatasets" :key="dataset._id">
          <v-tooltip top open-delay="1000">
            <span>{{dataset.name}}</span>
            <v-chip slot="activator" outline close color="primary" class='dataset'
              @input="removeDataset(dataset)"
              @mouseenter.native="setSelectedDataset(dataset)"
              @mouseleave.native="setSelectedDataset(null)"
            ><span>{{dataset.name}}</span></v-chip>
          </v-tooltip>
        </div>
      </SlideFadeGroup>
    </transition>
    <v-expansion-panel class="conditions" expand :value="[true]">
      <v-expansion-panel-content>
        <div slot='header'>Conditions</div>
        <v-list dense>
          <v-list-tile
            v-for="(condition,i) in this.editingConditions"
            :key="i"
            class="hover-show-parent"
            @mouseenter.native="setSelectedCondition(condition)"
            @mouseleave.native="setSelectedCondition(null)">
            <v-list-tile-avatar>
              <v-icon>aspect_ratio</v-icon>
            </v-list-tile-avatar>
            <v-list-tile-content>
              <v-list-tile-title>{{condition.type}}</v-list-tile-title>
            </v-list-tile-content>
            <v-list-tile-action class="hover-show-child">
              <v-menu offset-y absolute :nudge-bottom="20" :nudge-left="20">
                <v-btn class="group-menu-button" slot="activator" flat icon>
                  <v-icon color="grey darken-1">more_vert</v-icon>
                </v-btn>
                <v-list>
                  <v-list-tile @click="clientDownloadJSON(condition.geojson)">
                    <v-list-tile-title>Download as GeoJSON</v-list-tile-title>
                  </v-list-tile>
                </v-list>
              </v-menu>
            </v-list-tile-action>
            <v-list-tile-action @click='deleteCondition(condition)'>
              <v-btn icon ripple>
                <v-icon color="grey darken-1">delete</v-icon>
              </v-btn>
            </v-list-tile-action>
          </v-list-tile>
        </v-list>
      </v-expansion-panel-content>
    </v-expansion-panel>
    <div>
      <v-container grid-list-lg class="py-2">
        <v-layout>
          <v-flex xs3>
            <v-btn block depressed color='error'
              :disabled="!editingWorkingSet._id"
              @click="deleteRecord">
              <v-icon>delete</v-icon>
            </v-btn>
          </v-flex>
          <v-flex xs4>
            <v-btn block outline color='error' @click="exit">
              Cancel
            </v-btn>
          </v-flex>
          <v-flex xs5>
            <v-btn block depressed color='primary'
              :disabled="!name||!datasets.length"
              @click="save">
              Save
              <v-icon class='ml-1'>save</v-icon>
            </v-btn>
          </v-flex>
        </v-layout>
      </v-container>
    </div>
    <v-dialog
      :value="uploadGeojsonDialog"
      @input="setUploadGeojsonDialog($event)"
      max-width="290">
      <v-card>
        <v-card-title class="title">Upload a geojson file</v-card-title>
        <v-card-text>
          Select or drop a geojson file to be used region filter
          <FeatureSelector
            v-model="uploadFeatures"
            @message="prompt({message:$event})" />
        </v-card-text>
        <v-card-actions>
          <v-layout>
            <v-flex class="text-xs-center"><v-btn color="primary" :disabled="!uploadFeatures" @click="uploadGeojson">Upload</v-btn></v-flex>
          </v-layout>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { mapState, mapMutations, mapActions } from "vuex";
import SlideFadeGroup from "resonantgeoview/src/components/transition/slide-fade-group";

import FeatureSelector from "./FeatureSelector";
import clientDownloadJSON from "../utils/clientDownloadJSON";

export default {
  name: "EditWorkingSet",
  components: {
    FeatureSelector,
    SlideFadeGroup
  },
  props: {},
  data() {
    return {
      clientDownloadJSON,
      portal: {
        name: "title",
        text: "Edit Working set"
      },
      name: null,
      filterId: null,
      uploadFeatures: null
    };
  },
  computed: {
    regionFilters() {
      return this.workingSet.filters.filter(filter => filter.type === "region");
    },
    dateRangeFilters() {
      return this.workingSet.filters.filter(
        filter => filter.type === "daterange"
      );
    },
    undoSnackbar: {
      get: function() {
        return !!this.undoMessage;
      },
      set: function(value) {
        if (!value) {
          this.undoMessage = null;
        }
      }
    },
    filteredDatasets() {
      if (!this.datasets) {
        return;
      } else {
        return this.datasets.filter(dataset => !dataset.name.endsWith(".tar"));
      }
    },
    ...mapState("workingSet", [
      "editingWorkingSet",
      "datasets",
      "selectedDataset",
      "selectedCondition",
      "editingConditions",
      "uploadGeojsonDialog"
    ])
  },
  watch: {
    filterId(filterId) {
      if (!this.initialized) {
        return;
      }
      if (!filterId) {
        return;
      }
      this.loadDatasets(filterId);
    },
    editingConditions(editingConditions) {
      if (!this.initialized) {
        return;
      }
      this.loadDatasetByFilterConditions(editingConditions);
    }
  },
  async created() {
    this.name = this.editingWorkingSet.name;
    this.filterId = this.editingWorkingSet.filterId;
    let ps = [];
    if (this.editingWorkingSet._id) {
      ps.push(this.loadDatasetByWorkingSetId(this.editingWorkingSet._id));
    }
    if (this.filterId) {
      ps.push(this.loadConditionsByFilter(this.filterId));
    }
    await Promise.all(ps);
    this.initialized = true;
  },
  methods: {
    exit() {
      this.clear();
    },
    async save() {
      let filter = await this.saveFilter({
        id: this.filterId,
        name: this.name,
        conditions: this.editingConditions
      });
      this.saveWorkingSet({
        _id: this.editingWorkingSet._id,
        name: this.name,
        filterId: filter._id,
        datasetIds: this.datasets.map(dataset => dataset._id)
      }).then(workingSet => {
        Object.assign(this.editingWorkingSet, workingSet);
        this.exit();
      });
    },
    deleteRecord() {
      this.deleteWorkingSet(this.editingWorkingSet).then(() => {
        this.exit();
      });
    },
    removeDataset(dataset) {
      this.datasets.splice(this.datasets.indexOf(dataset), 1);
      this.setSelectedDataset(null);
    },
    uploadGeojson() {
      for (let feature of this.uploadFeatures) {
        this.editingConditions.push({
          type: "region",
          geojson: feature
        });
      }
      this.uploadFeatures = null;
      this.geojsonFilename = null;
      this.setUploadGeojsonDialog(false);
    },
    deleteCondition(filter) {
      this.setSelectedCondition(null);
      var index = this.editingConditions.indexOf(filter);
      this.editingConditions.splice(index, 1);
      this.prompt({
        message: "Condition deleted",
        button: "undo"
      }).then(result => {
        if (result === "undo") {
          this.editingConditions.splice(index, 0, filter);
        }
      });
    },
    ...mapActions("prompt", ["prompt"]),
    ...mapActions(["saveWorkingSet", "saveFilter", "deleteWorkingSet"]),
    ...mapActions("workingSet", [
      "loadDatasetByFilterConditions",
      "loadDatasetByWorkingSetId",
      "loadConditionsByFilter"
    ]),
    ...mapMutations("workingSet", [
      "setSelectedCondition",
      "setSelectedDataset",
      "setUploadGeojsonDialog",
      "clear"
    ])
  }
};
</script>

<style lang="scss" scoped>
.edit-workingset {
  display: flex;
  flex-direction: column;
  height: 100%;

  .datasets {
    overflow-y: auto;
    overflow-x: hidden;

    .dataset {
      width: calc(100% - 8px);
    }
  }

  .conditions {
    flex-shrink: 0;
  }
}

// overwrite
.v-expansion-panel {
  box-shadow: none;
}
</style>

<style lang="scss">
.edit-workingset {
  .datasets {
    .v-chip {
      span.v-chip__content {
        width: 100%;
        span {
          width: calc(100% - 20px);
          overflow-x: hidden;
        }
      }
    }
  }

  .conditions {
    .v-list__tile__action {
      min-width: 40px;
      padding: 0 8px;
    }
  }
}
</style>
