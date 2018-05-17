

<template>
  <FullScreenViewport>
    <GeojsMapViewport
      class='map'
      :viewport.sync='viewport'
    >
      <GeojsTileLayer
        url='https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png'
        attribution='© OpenStreetMap contributors, © CARTO'>
      </GeojsTileLayer>
      <GeojsAnnotationLayer
        :drawing.sync='drawing'
        :editing.sync='editing'
        :editable='true'
        :annotations.sync='edit.annotations'>
      </GeojsAnnotationLayer>
      <GeojsGeojsonLayer
        :geojson='editingWorkingSetAllRegionFilters'>
      </GeojsGeojsonLayer>
      <GeojsGeojsonLayer 
        v-if='editingWorkingSetSelectedRegionFilters'
        :geojson='editingWorkingSetSelectedRegionFilters'
        :featureStyle='{polygon:{fillColor:"red"}}'>
      </GeojsGeojsonLayer>
    </GeojsMapViewport>

    <SidePanel
    :top='64'
    :toolbar='{title: "Working Sets"}'
    :expanded='true'
    :footer='false'
    >
      <template slot='actions'>
        <SidePanelAction
        v-for="action in actions" 
        :key='action.name'
        @click.stop='clickAction(action.name)'>
        <v-icon>{{action.icon}}</v-icon>
        </SidePanelAction>
      </template>
      <v-expansion-panel v-if='!edit.workingSet'>
        <v-expansion-panel-content
          v-for="workingSet in workingSets" 
          :key="workingSet.name">
          <div slot='header'>{{workingSet.name}}</div>
          <v-container grid-list-xs>
            <v-layout row wrap>
              <v-flex xs2 offset-xs1>
                <v-btn block color='grey lighten-3' depressed @click="edit.workingSet=workingSet">
                  <v-icon>edit</v-icon>
                </v-btn>
              </v-flex>
              <v-flex xs4 offset-xs4>
                <v-btn block color='primary' class='' depressed @click="focusWorkingSet(workingSet)">
                  Focus
                  <v-icon class='pl-1'>center_focus_strong</v-icon>
                </v-btn>
              </v-flex>
            </v-layout>
          </v-container>
        </v-expansion-panel-content>
      </v-expansion-panel>
      <new-working-set v-if='!edit.workingSet' default='working-set-1' @confirm='addNewWorkingSet' />
      <EditWorkingSet 
      v-if='edit.workingSet'
      :annotations.sync='edit.annotations'
      :workingSet.sync='edit.workingSet'
      :selectedFilter.sync='edit.selectedFilter'
      :pickDataRange.sync='edit.pickDateRange' />
    </SidePanel>
  </FullScreenViewport>
</template>

<style lang="scss" scoped>
.map {
  z-index: 0;
}
// overwrite
.expansion-panel {
  box-shadow: none;
}
</style>
<script>
import { mapState } from "vuex";

import NewWorkingSet from "../components/NewWorkingSet";
import EditWorkingSet from "../components/EditWorkingSet";

export default {
  name: "explore",
  components: {
    NewWorkingSet,
    EditWorkingSet
  },
  data() {
    return {
      edit: {
        workingSet: null,
        selectedFilter: null,
        annotations: [],
        pickDateRange: false
      },
      viewport: {
        center: [-100, 30],
        zoom: 4
      },
      drawing: false,
      editing: false
    };
  },
  computed: {
    actions() {
      if (this.edit.workingSet) {
        return [
          { name: "rectangle", icon: "aspect_ratio" },
          { name: "daterange", icon: "date_range" }
        ];
      }
      return [];
    },
    editingWorkingSetAllRegionFilters() {
      if (!this.edit.workingSet) {
        return null;
      }
      return {
        type: "FeatureCollection",
        features: this.edit.workingSet.filters
          .filter(
            filter =>
              filter.type === "region" && filter !== this.edit.selectedFilter
          )
          .map(filter => filter.geojson)
      };
    },
    editingWorkingSetSelectedRegionFilters() {
      if (
        !this.edit.workingSet ||
        !this.edit.selectedFilter ||
        this.edit.selectedFilter.type !== "region"
      ) {
        return null;
      }
      return this.edit.selectedFilter.geojson;
    },
    ...mapState(["workingSets"])
  },
  created() {
    this.$store.dispatch("loadWorkingSets");
  },
  methods: {
    clickAction(name) {
      switch (name) {
        case "rectangle":
          this.drawing = name;
          break;
        case "daterange":
          this.edit.pickDateRange = true;
          break;
      }
    },
    clearItems() {
      this.panel.items = 0;
    },
    addNewWorkingSet(name) {
      this.$store.dispatch("tryAddWorkingSets", name).then(workingSet => {
        if (workingSet) {
          this.edit.workingSet = workingSet;
        }
      });
    },
    focusWorkingSet(workingSet) {
      this.$store.commit("selectWorkingSetId", workingSet._id);
      this.$router.push("focus");
    }
  }
};
</script>
