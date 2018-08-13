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
              <v-chip outline color="primary" 
                v-for="(dataset, i) in datasets" 
                :key="i"
                @mouseenter.native="setSelectedDataset(dataset)"
                @mouseleave.native="setSelectedDataset(null)"
              >{{dataset.name}}</v-chip>
            </div>
          </v-flex>
        </transition>
      </v-layout>
    </div>
    <v-expansion-panel class="conditions" expand :value="[true]">
      <v-expansion-panel-content>
        <div slot='header'>Conditions</div>
          <v-expansion-panel>
            <v-expansion-panel-content
              expand-icon="arrow_drop_down"
              v-for="(condition,i) in this.editingConditions"
              :key="i"
              @mouseenter.native="setSelectedCondition(condition)"
              @mouseleave.native="setSelectedCondition(null)">
              <div slot='header'><v-icon class="mr-2">{{getConditionIcon(condition)}}</v-icon><span :style="{position:'relative',top:'-3px'}">{{getConditionText(condition.type)}}</span><v-icon class="condition-delete" @click.stop='deleteCondition(condition)'>delete</v-icon></div>
              <v-card>
                <v-card-text class="text-xs-center p">
                  <DateRangeControl v-if="condition.type==='daterange'"
                    :start.sync='condition.start'
                    :end.sync='condition.end'
                  />
                  <div v-else>
                    Expansion panel content for item {{condition.type}}
                  </div>
                </v-card-text>
              </v-card>
            </v-expansion-panel-content>
          </v-expansion-panel>
      </v-expansion-panel-content>
    </v-expansion-panel>
    <div class='bottom'>
      <v-container grid-list-xs class="pa-0">
        <v-layout>
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
  </div>
</template>

<script>
import { mapState, mapMutations } from "vuex";

import DateRangeControl from "./DateRangeControl";

export default {
  name: "EditFilter",
  components: {
    DateRangeControl
  },
  props: {},
  data() {
    return {
      dateRangeFilter: {
        start: null,
        end: null
      },
      name: null
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
      "datasets"
    ])
  },
  watch: {
    annotations([annotation]) {
      if (annotation && annotation.geojson()) {
        this.editingConditions.push({
          type: "region",
          geojson: annotation.geojson()
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
      this.$store
        .dispatch("prompt/prompt", {
          message: "Condition deleted",
          button: "undo"
        })
        .then(result => {
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
    ...mapMutations("filter", [
      "setSelectedCondition",
      "setSelectedDataset"
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

    .conditions {
      .condition-delete {
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
</style>
