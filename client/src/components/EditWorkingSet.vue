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
              hint="A unique name for the working set"
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
            <v-flex xs12 class='datasets' v-if="datasets.length">
              <div class='body-2'>Datasets</div>
              <transition-group name="dataset" tag="div">
                <div v-for="dataset in datasets" :key="dataset._id" class="dataset-item">
                  <v-chip outline close color="primary" class='dataset'
                    @input="removeDataset(dataset)"
                    @mouseenter.native="setSelectedDataset(dataset)"
                    @mouseleave.native="setSelectedDataset(null)"
                  ><span>{{dataset.name}}</span></v-chip>
                </div>
              </transition-group>
            </v-flex>
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
  </div>
</template>

<script>
import { mapState, mapMutations } from "vuex";

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
      name: null,
      filterId: null
    };
  },
  created() {
    this.name = this.editingWorkingSet.name;
    this.filterId = this.editingWorkingSet.filterId;
    if (this.filterId && this.editingWorkingSet.datasetIds.length === 0) {
      this.loadDatasets(this.filterId);
    } else {
      loadDatasetById(this.editingWorkingSet.datasetIds).then(datasets => {
        this.initialized = true;
        this.$store.commit("workingSet/setDatasets", datasets);
      });
    }
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
    ...mapState(["filters"]),
    ...mapState("workingSet", [
      "editingWorkingSet",
      "datasets",
      "selectedDataset"
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
    }
  },
  methods: {
    exit() {
      this.$store.commit("workingSet/setDatasets", []);
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
    deleteRecord() {
      this.$store
        .dispatch("deleteWorkingSet", this.editingWorkingSet)
        .then(() => {
          this.exit();
        });
    },
    loadDatasets(filterId) {
      this.$store.commit("workingSet/setDatasets", []);
      var filter = this.filters.filter(filter => filter._id === filterId)[0];
      loadDatasetByFilterConditions(filter.conditions).then(datasets => {
        this.$store.commit("workingSet/setDatasets", datasets);
      });
    },
    removeDataset(dataset) {
      this.datasets.splice(this.datasets.indexOf(dataset), 1);
      this.setSelectedDataset(null);
    },
    ...mapMutations("workingSet", ["setSelectedDataset"])
  }
};
</script>

<style lang="scss" scoped>
.edit-workingset {
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
      width: 100%;
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
.dataset-enter, .dataset-leave-to
/* .dataset-leave-active below version 2.1.8 */ {
  opacity: 0;
  transform: translateX(30px);
}
.dataset-leave-active {
  position: absolute;
  width: 100%;
}
</style>

<style lang="scss">
.datasets {
  .chip {
    .chip__content {
      span {
        width: calc(100% - 20px);
        overflow-x: hidden;
      }
    }
  }
}
</style>
