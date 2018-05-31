<template>
  <div class='edit-filter'>
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
      </v-container>
      <v-expansion-panel class='conditions'>
        <v-expansion-panel-content :value='true'>
          <div slot='header'>Conditions</div>
            <v-expansion-panel>
              <v-expansion-panel-content
                expand-icon="arrow_drop_down"
                v-for="(condition,i) in this.editingConditions" 
                :key="i" @mouseenter.native="setSelectedCondition(condition)" @mouseleave.native="setSelectedCondition(null)">
                <div slot='header'><v-icon class="mr-2">{{getConditionIcon(condition)}}</v-icon>{{getConditionText(condition.type)}}<v-icon class="condition-delete" @click.stop='deleteCondition(condition)'>delete</v-icon></div>
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
.edit-filter {
  height: 100%;
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
.expansion-panel {
  box-shadow: none;
}
</style>

<script>
import { mapState } from "vuex";

import loadDataset from "../utils/loadDataset";
import DateRangeControl from "./DateRangeControl";

export default {
  name: "EditFilter",
  components: {
    DateRangeControl
  },
  props: {},
  data() {
    return {
      undoMessage: null,
      undoAction: null,
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
    ...mapState("filter", [
      "editingFilter",
      "selectedCondition",
      "editingConditions",
      "annotations",
      "pickDateRange"
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
      this.undoAction = () => {
        this.editingConditions.splice(index, 0, filter);
      };
      this.undoMessage = "Filter deleted";
    },
    deleteRecord() {
      this.$store.dispatch("deleteFilter", this.editingFilter).then(() => {
        this.exit();
      });
    },
    setSelectedCondition(condition) {
      this.$store.commit("filter/setSelectedCondition", condition);
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
    }
  }
};
</script>
