<template>
  <div class='edit-workingset'>
    <div class='main'>
      <v-container grid-list-md>
        <v-layout row wrap>
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
        <v-layout row wrap>
          <v-flex>
            <v-select
              :items="filters"
              v-model="filterId"
              label="Filter"
              item-text="name"
              item-value='_id'
            ></v-select>
          </v-flex>
        </v-layout>
        <v-layout row wrap>
          <transition name='fade'>
            <div class='datasets' v-if="datasets.length">
              <div class='body-2'>Datasets</div>
              <transition-group name="dataset" tag="div">
                <v-flex v-for="dataset in datasets" :key="dataset._id" class="dataset-item">
                  <v-chip outline close color="primary" class='dataset' @input="removeDataset(dataset)">{{dataset.name}}</v-chip>
                </v-flex>
              </transition-group>
            </div>
          </transition>
        </v-layout>
      </v-container>
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

//transition

.dataset-item {
  transition: all 0.15s;
}
.dataset-enter, .dataset-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
.dataset-leave-active {
  position: absolute;
  width: 100%;
}
</style>

<script>
import { mapState } from "vuex";

import {
  loadDatasetById,
  loadDatasetByFilterConditions
} from "../utils/loadDataset";
import DateRangeControl from "./DateRangeControl";

export default {
  name: "EditWorkingSet",
  components: {
    DateRangeControl
  },
  props: {},
  data() {
    return {
      datasets: [],
      undoMessage: null,
      undoAction: null,
      name: null,
      filterId: null
    };
  },
  created() {
    this.name = this.editingWorkingSet.name;
    this.filterId = this.editingWorkingSet.filterId;
    loadDatasetById(this.editingWorkingSet.datasetIds).then(datasets => {
      this.initialized = true;
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
    },
    ...mapState(["filters"]),
    ...mapState("workingSet", ["editingWorkingSet"])
  },
  watch: {
    filterId(filterId) {
      if (!this.initialized) {
        return;
      }
      if (!filterId) {
        return;
      }
      this.datasets = [];
      var filter = this.filters.filter(filter => filter._id === filterId)[0];
      loadDatasetByFilterConditions(filter.conditions).then(datasets => {
        this.datasets = datasets;
      });
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
      this.$store.commit("workingSet/setEditingWorkingSet", null);
    },
    save() {
      this.$store
        .dispatch("saveWorkingSet", {
          _id: this.editingWorkingSet._id,
          name: this.name,
          filterId: this.filterId,
          datasetIds: this.datasets.map(dataset => dataset._id)
        })
        .then(workingSet => {
          Object.assign(this.editingWorkingSet, workingSet);
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
      this.$store
        .dispatch("deleteWorkingSet", this.editingWorkingSet)
        .then(() => {
          this.exit();
        });
    },
    setSelectedFilter(filter) {
      this.$emit("update:selectedFilter", filter);
    },
    createDataRangeFilter() {
      this.closeDataRangeDialog(false);
      this.workingSet.filters.push({
        type: "daterange",
        start: this.dateRangeFilter.start,
        end: this.dateRangeFilter.end
      });
    },
    removeDataset(dataset) {
      this.datasets.splice(this.datasets.indexOf(dataset), 1);
    }
  }
};
</script>
