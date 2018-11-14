/*#############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
#############################################################################*/

<template>
  <div class="full-screen">
    <GeojsMapViewport
      class="map"
      :viewport.sync="viewport"
      :zoomRange="{ min: 0, max: 18 }">
      <GeojsTileLayer
        url='https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png'
        attribution='© OpenStreetMap contributors, © CARTO'
        :zIndex='0'>
      </GeojsTileLayer>
      <GeojsHeatmapLayer v-if="!editingWorkingSet && viewport.zoom<=7"
        :data="heatmapData"
        :binned="10"
        :maxIntensity="5"
        :minIntensity="0"
        :updateDelay="100"
        :zIndex="1">
      </GeojsHeatmapLayer>
      <GeojsGeojsonLayer
        v-if="editingWorkingSet || viewport.zoom>7"
        :geojson="datasetBoundsFeature"
        :featureStyle="datasetBoundsFeatureStyle"
        :zIndex="2">
      </GeojsGeojsonLayer>
      <template v-if="exploreTab==='filter'">
        <GeojsAnnotationLayer
          :drawing.sync="drawing"
          :editing.sync="editing"
          :editable="true"
          :annotations="annotations"
          @update:annotations="$store.commit('filter/setAnnotations',$event)"
          :zIndex="3">
        </GeojsAnnotationLayer>
        <GeojsGeojsonLayer 
          v-if="editingConditionsGeojson"
          :geojson="editingConditionsGeojson"
          :featureStyle="filterGeojsonLayerStyle"
          :zIndex="4">
        </GeojsGeojsonLayer>
      </template>
      <template v-if="combinedSelectedDatasetPoint">
        <GeojsGeojsonLayer
          :geojson="combinedSelectedDatasetPoint"
          :featureStyle="{point:{strokeColor:'black',strokeWidth:2,radius:3}}"
          :zIndex="5">
        </GeojsGeojsonLayer>
        <GeojsWidgetLayer
          :position="combinedSelectedDatasetPoint.coordinates"
          :offset="{x:0,y:-20}"
          :zIndex="6">
          <v-chip small color="green" text-color="white">{{combinedSelectedDataset.name}}</v-chip>
        </GeojsWidgetLayer>
      </template>
    </GeojsMapViewport>

    <SidePanel
      class="side-panel"
      :top="64"
      :floating='false'
      :toolbar="{title}"
      :expanded='sidePanelExpanded'
      :footer="false">
      <template slot="actions">
        <SidePanelAction
        v-for="action in actions" 
        :key="action.name"
        @click.stop="clickAction(action.name)">
        <v-icon>{{action.icon}}</v-icon>
        </SidePanelAction>
      </template>
      <div class="main">
        <transition name="slide-fade" mode="out-in">
          <WorkingSetModule 
            v-if="exploreTab==='workingSet'" />
          <FilterModule 
            v-if="exploreTab==='filter'" />
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
    <Logo />
  </div>
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

.logo {
  left: 3px;
  bottom: 0px;
}
</style>
<script>
import { mapState, mapGetters } from "vuex";
import pointOnFeature from "@turf/point-on-feature";

import WorkingSetModule from "./WorkingSetModule";
import FilterModule from "./FilterModule";
import Logo from "../components/Logo";

export default {
  name: "Explore",
  components: {
    WorkingSetModule,
    FilterModule,
    Logo
  },
  data() {
    return {
      viewport: {
        center: [-95, 40],
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
          { name: "polygon", icon: "label_outline" },
          { name: "upload-geojson", icon: "fa-file-upload" }
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
    filterGeojsonLayerStyle() {
      // Tell Vuejs selectedCondition is a dependancy of this computed
      var selectedCondition = this.selectedCondition;
      var primaryColor = this.$vuetify.theme.primary;
      return {
        polygon: {
          strokeColor: "#000000",
          strokeOpacity: 0.75,
          fillOpacity: 0.25,
          fillColor: (a, b, data) => {
            return selectedCondition && data === selectedCondition.geojson
              ? "red"
              : primaryColor;
          }
        }
      };
    },
    heatmapData() {
      var datasets = this.editingWorkingSet
        ? this.workingSetDatasets
        : this.editingFilter
          ? this.filterDatasets
          : this.allDatasets;
      if (!datasets) {
        return null;
      }
      return datasets.map(dataset => {
        let point = pointOnFeature(dataset.geometa.bounds);
        return point.geometry.coordinates;
      });
    },
    datasetBoundsFeature() {
      var datasets = this.editingWorkingSet
        ? this.workingSetDatasets
        : this.editingFilter
          ? this.filterDatasets
          : this.allDatasets;
      if (!datasets) {
        return null;
      }
      return datasets
        .filter(dataset => dataset["geometa"] && dataset["geometa"]["bounds"])
        .reduce(
          (featureCollection, dataset) => {
            featureCollection.features.push({
              type: "Feature",
              properties: {
                name: dataset.name,
                _id: dataset._id
              },
              geometry: dataset["geometa"]["bounds"]
            });
            return featureCollection;
          },
          { type: "FeatureCollection", features: [] }
        );
    },
    datasetBoundsFeatureStyle() {
      // Tell Vuejs combinedSelectedDataset is a dependancy of this computed
      var selectedDataset = this.combinedSelectedDataset;
      var primaryColor = this.$vuetify.theme.primary;
      return {
        polygon: {
          uniformPolygon: true,
          fill(data) {
            return selectedDataset &&
              selectedDataset._id === data.properties._id
              ? true
              : false;
          },
          fillColor: "red",
          fillOpacity: 0.2,
          strokeColor(a, b, data) {
            return selectedDataset &&
              selectedDataset._id === data.properties._id
              ? "red"
              : primaryColor;
          },
          strokeOpacity: 0.6,
          strokeWidth: 1.2
        }
      };
    },
    combinedSelectedDataset() {
      return (
        this.$store.state.workingSet.selectedDataset ||
        this.$store.state.filter.selectedDataset
      );
    },
    combinedSelectedDatasetPoint() {
      var selectedDataset = this.combinedSelectedDataset;
      if (!selectedDataset || !selectedDataset.geometa) {
        return null;
      }
      return pointOnFeature(selectedDataset.geometa.bounds).geometry;
    },
    ...mapState(["sidePanelExpanded", "exploreTab", "allDatasets"]),
    ...mapState("workingSet", ["editingWorkingSet"]),
    ...mapState("workingSet", {
      workingSetDatasets: "datasets"
    }),
    ...mapState("filter", [
      "editingFilter",
      "annotations",
      "selectedCondition"
    ]),
    ...mapState("filter", {
      filterDatasets: "datasets"
    }),
    ...mapGetters("filter", ["editingConditionsGeojson"]),
    user() {
      return this.$girder.user;
    }
  },
  watch: {
    user(user) {
      if (!user) {
        this.$router.push("/login");
      }
    }
  },
  created() {
    this.$store.dispatch("loadAllDatasets");
    this.$store.dispatch("loadWorkingSets");
    this.$store.dispatch("loadFilters");
  },
  mounted() {
    setTimeout(() => {
      // A fix that map container doesn't have correct size when map being initialized
      window.dispatchEvent(new Event("resize"));
    }, 100);
  },
  methods: {
    clickAction(name) {
      switch (name) {
        case "rectangle":
          this.drawing = this.drawing !== name ? name : null;
          break;
        case "polygon":
          this.drawing = this.drawing !== name ? name : null;
          break;
        // case "daterange":
        //   this.$store.commit("filter/setPickDateRange", true);
        //   break;
        case "upload-geojson":
          this.$store.commit("filter/setUploadGeojsonDialog", true);
          break;
      }
    }
  }
};
</script>
