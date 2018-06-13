

<template>
  <FullScreenViewport>
    <GeojsMapViewport
      class='map'
      :viewport.sync='viewport'
    >
      <GeojsTileLayer
        url='https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png'
        attribution='© OpenStreetMap contributors, © CARTO'
        :zIndex='0'>
      </GeojsTileLayer>
      <template v-if="exploreTab==='workingSet'">
        <GeojsAnnotationLayer
          :drawing.sync='drawing'
          :editing.sync='editing'
          :editable='true'
          :annotations='annotations'
          @update:annotations="$store.commit('filter/setAnnotations',$event)"
          :zIndex='4'>
        </GeojsAnnotationLayer>
      </template>
      <template v-if="exploreTab==='filter'">
        <GeojsAnnotationLayer
          :drawing.sync='drawing'
          :editing.sync='editing'
          :editable='true'
          :annotations='annotations'
          @update:annotations="$store.commit('filter/setAnnotations',$event)"
          :zIndex='4'>
        </GeojsAnnotationLayer>
        <GeojsGeojsonLayer
          v-if='editingConditionsGeojson'
          :geojson='editingConditionsGeojson'
          :zIndex='2'>
        </GeojsGeojsonLayer>
        <GeojsGeojsonLayer 
          v-if='editingSelectedConditionGeojson'
          :geojson='editingSelectedConditionGeojson'
          :featureStyle='{polygon:{fillColor:"red"}}'
          :zIndex='3'>
        </GeojsGeojsonLayer>
        <GeojsHeatmapLayer v-if="editingFilter"
          :data='heatmapData'
          :binned='10'
          :maxIntensity='5'
          :minIntensity='0'
          :updateDelay='100'
          :zIndex='1'>
        </GeojsHeatmapLayer>
      </template>
    </GeojsMapViewport>

    <SidePanel
    class='side-panel'
    :top='64'
    :toolbar='{title}'
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
      <div class='main'>
        <transition name="slide-fade" mode="out-in">
         <WorkingSetModule 
            v-if="exploreTab==='workingSet'"
           />
          <FilterModule 
            v-if="exploreTab==='filter'"
           />
        </transition>
      </div>
      <v-bottom-nav :value="true" :active="exploreTab" @update:active="$store.commit('setExploreTab',$event)" color="transparent">
        <v-btn flat color="primary" value="workingSet">
          <span>Working sets</span>
          <v-icon>history</v-icon>
        </v-btn>
        <v-btn flat color="primary" value="filter">
          <span>Filters</span>
          <v-icon>place</v-icon>
        </v-btn>
      </v-bottom-nav>
    </SidePanel>
  </FullScreenViewport>
</template>

<style lang="scss" scoped>
.map {
  z-index: 0;
}

.side-panel {
  display: flex;
  flex-direction: column;

  .main {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
  }
}
</style>
<script>
import { mapState, mapGetters } from "vuex";

import WorkingSetModule from "./WorkingSetModule";
import FilterModule from "./FilterModule";

import rest from "girder/src/rest";

export default {
  name: "explore",
  components: {
    WorkingSetModule,
    FilterModule
  },
  data() {
    return {
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
      if (this.editingFilter) {
        return [
          { name: "rectangle", icon: "aspect_ratio" },
          { name: "daterange", icon: "date_range" }
        ];
      }
      return [];
    },
    title() {
      switch (this.exploreTab) {
        case "workingSet":
          if (!this.editingWorkingSet) {
            return "Working Sets";
          } else {
            return "Edit Working Set";
          }
        case "filter":
          if (!this.editingFilter) {
            return "Filters";
          } else {
            return "Edit Filter";
          }
      }
    },
    ...mapState(["exploreTab"]),
    ...mapState("workingSet", ["editingWorkingSet"]),
    ...mapState("filter", [
      "editingFilter",
      "annotations",
      "selectedCondition"
    ]),
    ...mapGetters("filter", [
      "editingConditionsGeojson",
      "editingSelectedConditionGeojson",
      "heatmapData"
    ])
  },
  created() {
    this.$store.dispatch("loadWorkingSets");
    this.$store.dispatch("loadFilters");
    rest.get("item/geometa?bbox=-180,-90,180,90&relation=intersects").then(({ data }) => {
      console.log(data);
    });
  },
  methods: {
    clickAction(name) {
      switch (name) {
        case "rectangle":
          this.drawing = this.drawing !== name ? name : null;
          break;
        case "daterange":
          this.$store.commit("filter/setPickDateRange", true);
          break;
      }
    }
  }
};
</script>
