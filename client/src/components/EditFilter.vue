<template>
  <div class='edit-filter'>
    <div class='main ma-2'>
      <v-layout>
        <v-flex>
          <v-text-field
            class="input"
            name="Name"
            label="Name"
            hint="A unique name for the filter"
            v-model="name"
          ></v-text-field>
        </v-flex>
      </v-layout>
      <v-layout>
        <transition name='fade'>
          <v-flex xs12>
            <div class='datasets' v-if="datasets.length">
              <div class='body-2'>Datasets</div>
              <span v-for="dataset in datasets" :key="dataset._id">
                <v-tooltip top open-delay="1000">
                  <span>{{dataset.name}}</span>
                  <v-chip  slot="activator" outline color="primary" 
                    @mouseenter.native="setSelectedDataset(dataset)"
                    @mouseleave.native="setSelectedDataset(null)"
                  >{{dataset.name}}</v-chip>
                </v-tooltip>
              </span>
            </div>
          </v-flex>
        </transition>
      </v-layout>
    </div>
    <v-expansion-panel class="conditions" expand :value="[true]">
      <v-expansion-panel-content>
        <div slot='header'>Conditions</div>
        <v-list>
          <v-list-tile
            v-for="(condition,i) in this.editingConditions"
            :key="i"
            class="hover-show-parent"
            @mouseenter.native="setSelectedCondition(condition)"
            @mouseleave.native="setSelectedCondition(null)">
            <v-list-tile-avatar>
              <v-icon>{{getConditionIcon(condition)}}</v-icon>
            </v-list-tile-avatar>
            <v-list-tile-content>
              <v-list-tile-title>{{getConditionText(condition.type)}}</v-list-tile-title>
            </v-list-tile-content>
            <v-list-tile-action class="hover-show-child">
              <v-menu offset-y absolute :nudge-bottom="20" :nudge-left="20">
                <v-btn class="group-menu-button" slot="activator" flat icon>
                  <v-icon color="grey darken-1">more_vert</v-icon>
                </v-btn>
                <v-list>
                  <v-list-tile @click="downloadRegionFilter(condition.geojson)">
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
    <div class='bottom'>
      <v-container grid-list-lg class="py-2">
        <v-layout>
          <v-flex xs3>
            <v-btn block depressed color='error'
              :disabled="!editingFilter._id"
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
              :disabled="!name"
              @click="save">
              Save
              <v-icon class='ml-1'>save</v-icon>
            </v-btn>
          </v-flex>
        </v-layout>
      </v-container>
    </div>
    <v-dialog 
      :value="pickDateRange" 
      @input="closeDataRangeDialog($event)" 
      max-width="350"
      lazy>
      <v-card>
        <v-card-title class="headline">Create date range filter</v-card-title>
        <v-card-text><DateRangeControl 
        :start.sync='dateRangeFilter.start'
        :end.sync='dateRangeFilter.end'
        /></v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="error" flat @click="createDataRangeFilter()">Cancel</v-btn>
          <v-btn color="primary" @click="createDataRangeFilter()">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
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

import DateRangeControl from "./DateRangeControl";
import FeatureSelector from "./FeatureSelector";

export default {
  name: "EditFilter",
  components: {
    DateRangeControl,
    FeatureSelector
  },
  props: {},
  data() {
    return {
      portal: {
        name: "title",
        text: "Edit Filter"
      },
      name: null,
      dateRangeFilter: {
        start: null,
        end: null
      },
      geojsonFilename: "",
      uploadFeatures: null
    };
  },
  computed: {
    regionFilters() {
      return this.editingFilter.conditions.filter(
        filter => filter.type === "region"
      );
    },
    dateRangeFilters() {
      return this.editingFilter.conditions.filter(
        filter => filter.type === "daterange"
      );
    },
    ...mapState("filter", [
      "editingFilter",
      "selectedCondition",
      "editingConditions",
      "annotations",
      "pickDateRange",
      "uploadGeojsonDialog",
      "datasets"
    ])
  },
  watch: {
    annotations([annotation]) {
      if (annotation && annotation.geojson()) {
        var geojson = annotation.geojson();
        delete geojson.properties;
        this.editingConditions.push({
          type: "region",
          geojson
        });
        this.$store.commit("filter/setAnnotations", []);
      }
    },
    pickDateRange(value) {
      if (value) {
        this.dateRangeFilter.start = null;
        this.dateRangeFilter.end = null;
      }
    },
    editingConditions(value) {
      this.$store.dispatch("filter/loadDatasets", this.editingConditions);
    }
  },
  created() {
    this.name = this.editingFilter.name;
    this.$store.commit(
      "filter/setEditingConditions",
      this.editingFilter.conditions.slice()
    );
  },
  methods: {
    getConditionIcon(filter) {
      switch (filter.type) {
        case "region":
          return "aspect_ratio";
        case "daterange":
          return "date_range";
      }
    },
    getConditionText(type) {
      switch (type) {
        case "region":
          return type;
        case "daterange":
          return "Date range";
      }
    },
    exit() {
      this.$store.commit("filter/setEditingFilter", null);
      this.$store.commit("filter/setDatasets", []);
    },
    save() {
      this.$store
        .dispatch("saveFilter", {
          _id: this.editingFilter._id,
          name: this.name,
          conditions: this.editingConditions
        })
        .then(filter => {
          this.exit();
        });
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
    deleteRecord() {
      this.$store.dispatch("deleteFilter", this.editingFilter).then(() => {
        this.exit();
      });
    },
    closeDataRangeDialog(value) {
      this.$store.commit("filter/setPickDateRange", value);
    },
    createDataRangeFilter() {
      this.closeDataRangeDialog(false);
      this.editingConditions.push({
        type: "daterange",
        start: this.dateRangeFilter.start,
        end: this.dateRangeFilter.end
      });
    },
    async onGeojsonSelected(file) {
      if (!file) {
        this.uploadFeatures = null;
        return;
      }
      try {
        this.uploadFeatures = await this.tryGetFeaturesFromFile(file);
      } catch (ex) {
        this.uploadFeatures = null;
        this.prompt({ message: ex.message });
      }
    },
    async tryGetFeaturesFromFile(file) {
      if (file.size > 1024 * 1024) {
        throw new Error("File is too large");
      }
      var result = await new Promise((resolve, reject) => {
        var reader = new FileReader();
        reader.onload = e => {
          resolve(reader.result);
        };
        reader.readAsText(file);
      });
      var geojson = JSON.parse(result);
      var features = null;
      if (geojson.features) {
        features = geojson.features;
      } else if (geojson.geometries) {
        features = geojson.geometries.map(geometry => ({
          type: "Feature",
          geometry
        }));
      } else if (geojson.coordinates) {
        features = [
          {
            type: "Feature",
            geometry: geojson
          }
        ];
      } else {
        features = [geojson];
      }
      features = features.filter(
        feature => feature.geometry && feature.geometry.type === "Polygon"
      );
      if (!features.length) {
        throw new Error("File doesn't contain a valid polygon feature");
      }
      if (features.length > 5) {
        throw new Error("File has more than 5 polygon features");
      }
      return features;
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
    downloadRegionFilter(geojson) {
      var a = window.document.createElement("a");
      a.href = window.URL.createObjectURL(
        new Blob([JSON.stringify(geojson)], { type: "application/json" })
      );
      a.download = "filter.geojson";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    },
    ...mapActions("prompt", ["prompt"]),
    ...mapMutations("filter", [
      "setSelectedCondition",
      "setSelectedDataset",
      "setUploadGeojsonDialog"
    ])
  }
};
</script>

<style lang="scss" scoped>
.edit-filter {
  display: flex;
  flex-direction: column;

  .main {
    flex: 1;
  }

  .bottom {
    .btn {
      min-width: 0;
    }
  }
}

// overwrite
.v-expansion-panel {
  box-shadow: none;
}
</style>

<style lang="scss">
.datasets {
  .v-chip {
    max-width: 100%;

    .v-chip__content {
      max-width: 100%;
      overflow-x: hidden;
    }
  }
}

.conditions {
  .v-list__tile__action {
    min-width: 40px;
    padding: 0 8px;
  }
}
</style>
