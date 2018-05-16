<template>
  <div class='edit-workingset'>
    <div class='main'>
      <div class='datasets'>
        <v-container grid-list-xs>
          <v-layout row wrap>
            <v-flex xs10 offset-xs1 v-for="dataset in datasets" :key="dataset._id">
              <v-chip class='dataset grey lighten-3'>{{dataset.name}}</v-chip>
            </v-flex>
          </v-layout>
        </v-container>
      </div>
      <v-expansion-panel class='filters'>
        <v-expansion-panel-content :value='true'>
          <div slot='header'>Filters</div>
            <v-expansion-panel>
              <v-expansion-panel-content
                expand-icon="arrow_drop_down"
                v-for="(filter,i) in workingSet.filters" 
                :key="i">
                <div slot='header'><v-icon class="mr-2">{{getFilterIcon(filter)}}</v-icon>{{filter.type}}<v-icon class="filter-delete" @click='workingSet.filters.splice(i, 1)'>delete</v-icon></div>
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

export default {
  name: "EditWorkingSet",
  props: {
    workingSet: {
      type: Object,
      default: null
    },
    annotations: {
      type: Array,
      default: []
    }
  },
  data() {
    return {
      datasets: []
    };
  },
  created() {
    loadDataset().then(datasets => {
      this.datasets = datasets;
    });
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
    }
  },
  methods: {
    getFilterIcon(filter) {
      switch (filter.type) {
        case "region":
          return "aspect_ratio";
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
    deleteRecord() {
      this.$store.dispatch("deleteWorkingSet", this.workingSet).then(() => {
        this.exit();
      });
    }
  }
};
</script>
