<template>
  <div class='edit-workingset'>
    <div class='main'>
      <div class='datasets'>
        <transition name='fade'>
          <v-container grid-list-xs v-if="datasets.length">
            <v-layout row wrap>
              <v-flex xs10 offset-xs1 v-for="dataset in datasets" :key="dataset._id">
                <v-chip class='dataset grey lighten-3'>{{dataset.name}}</v-chip>
              </v-flex>
            </v-layout>
          </v-container>
        </transition>
      </div>
      <v-expansion-panel class='filters'>
        <v-expansion-panel-content :value='true'>
          <div slot='header'>Filters</div>
            <v-expansion-panel>
              <v-expansion-panel-content
                expand-icon="arrow_drop_down"
                v-for="(filter,i) in workingSet.filters" 
                :key="i" @mouseenter.native="setSelectedFilter(filter)" @mouseleave.native="setSelectedFilter(null)">
                <div slot='header'><v-icon class="mr-2">{{getFilterIcon(filter)}}</v-icon>{{getFilterDisplayType(filter)}}<v-icon class="filter-delete" @click.stop='deleteFilter(filter)'>delete</v-icon></div>
                <v-card>
                  <v-card-text class="text-xs-center">
                    Expansion panel content for item {{filter.type}}
                  </v-card-text>
                </v-card>
              </v-expansion-panel-content>
            </v-expansion-panel>
        </v-expansion-panel-content>
      </v-expansion-panel>
    </div>
    <div class='bottom py-3'>
      <v-container grid-list-xs>
        <v-layout row wrap>
          <v-flex xs2 offset-xs1>
            <v-btn block depressed color='error' class='' @click="deleteRecord">
              <v-icon>delete</v-icon>
            </v-btn>
          </v-flex>
          <v-flex xs3 offset-xs1>
            <v-btn block outline color='error' class='' @click="exit">
              Cancel
            </v-btn>
          </v-flex>
          <v-flex xs3 offset-xs1>
            <v-btn block depressed color='primary' class='' @click="save">
              Save
              <v-icon class='ml-1'>save</v-icon>
            </v-btn>
          </v-flex>
        </v-layout>
      </v-container>
    </div>
    <v-dialog 
      :value="pickDataRange" 
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
    <v-snackbar
        :timeout="3000"
        :bottom="true"
        v-model="undoSnackbar"
      >
        {{ undoMessage }}
        <v-btn flat color="pink" @click.native="undoAction();undoMessage=null;">Undo</v-btn>
      </v-snackbar>
  </div>
</template>

<style lang="scss" scoped>
.edit-workingset {
  height: 100%;
  display: flex;
  flex-direction: column;

  .main {
    flex: 1;
    display: flex;
    flex-direction: column;

    .datasets,
    .filters {
      flex: 1;
    }

    .datasets .dataset {
      display: block;
    }

    .filters {
      .filter-delete {
        float: right;
      }
    }
  }

  .bottom {
    .btn {
      min-width: 0;
    }
  }
}

// overwrite
.expansion-panel {
  box-shadow: none;
}
</style>

<script>
import loadDataset from "../utils/loadDataset";
import DateRangeControl from "./DateRangeControl";

export default {
  name: "EditWorkingSet",
  components: {
    DateRangeControl
  },
  props: {
    workingSet: {
      type: Object,
      default: null
    },
    selectedFilter: {
      type: Object,
      default: null
    },
    annotations: {
      type: Array,
      default: []
    },
    pickDataRange: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      datasets: [],
      undoMessage: null,
      undoAction: null,
      dateRangeFilter: {
        start: null,
        end: null
      }
    };
  },
  created() {
    loadDataset().then(datasets => {
      this.datasets = datasets;
    });
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
      // getter
      get: function() {
        return !!this.undoMessage;
      },
      // setter
      set: function(value) {
        if (!value) {
          this.undoMessage = null;
        }
      }
    }
  },
  watch: {
    annotations([annotation]) {
      if (annotation && annotation.geojson()) {
        this.workingSet.filters.push({
          type: "region",
          geojson: annotation.geojson()
        });
        this.$emit("update:annotations", []);
      }
    },
    pickDataRange(value) {
      if (value) {
        this.dateRangeFilter.start = null;
        this.dateRangeFilter.end = null;
      }
    }
  },
  methods: {
    getFilterIcon(filter) {
      switch (filter.type) {
        case "region":
          return "aspect_ratio";
        case "daterange":
          return "date_range";
      }
    },
    getFilterDisplayType(filter) {
      switch (filter.type) {
        case "region":
          return filter.type;
        case "daterange":
          return "Date range";
      }
    },
    exit() {
      this.$emit("update:workingSet", null);
    },
    save() {
      this.$store.dispatch("saveWorkingSet", this.workingSet).then(() => {
        this.exit();
      });
    },
    deleteFilter(filter) {
      this.setSelectedFilter(null);
      var index = this.workingSet.filters.indexOf(filter);
      this.workingSet.filters.splice(index, 1);
      this.undoAction = () => {
        this.workingSet.filters.splice(index, 0, filter);
      };
      this.undoMessage = "Filter deleted";
    },
    deleteRecord() {
      this.$store.dispatch("deleteWorkingSet", this.workingSet).then(() => {
        this.exit();
      });
    },
    setSelectedFilter(filter) {
      this.$emit("update:selectedFilter", filter);
    },
    closeDataRangeDialog(value) {
      this.$emit("update:pickDataRange", value);
    },
    createDataRangeFilter() {
      this.closeDataRangeDialog(false);
      this.workingSet.filters.push({
        type: "daterange",
        start: this.dateRangeFilter.start,
        end: this.dateRangeFilter.end
      });
    }
  }
};
</script>
