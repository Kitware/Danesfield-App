<template>
  <div class="vector-custom-viz-pane">
    <v-tabs
      grow
      v-model="currentTab"
      color="white">
      <v-tab key="point" :disabled="!summary.types.pointAlike">POINTS</v-tab>
      <v-tab key="line" :disabled="!summary.types.lineAlike">LINES</v-tab>
      <v-tab key="polygon" :disabled="!summary.types.polygonAlike">POLYGONS</v-tab>
      <v-tab-item key="point">
      </v-tab-item>
      <v-tab-item key="line">
        <v-card flat>
          <v-card-text>line</v-card-text>
        </v-card>
      </v-tab-item>
      <v-tab-item key="polygon">
        <Stroke :enabled.sync="vizProperties.polygon.stroke"
          :property.sync="vizProperties.polygon.strokeProperty"
          :properties="Object.keys(summary.properties)"
          :color.sync="vizProperties.polygon.strokeColor"
          :scheme.sync="vizProperties.polygon.strokeScheme"
          :opacity.sync="vizProperties.polygon.strokeOpacity"
          :width.sync="vizProperties.polygon.strokeWidth" />
        <Fill :enabled.sync="vizProperties.polygon.fill"
          :property.sync="vizProperties.polygon.fillProperty"
          :properties="Object.keys(summary.properties)"
          :color.sync="vizProperties.polygon.fillColor"
          :scheme.sync="vizProperties.polygon.fillScheme"
          :opacity.sync="vizProperties.polygon.fillOpacity"
          :scale.sync="vizProperties.polygon.fillScale" />
      </v-tab-item>
    </v-tabs>
    <v-container fluid grid-list-sm class="py-2 px-3">
      <v-layout align-center>
        <v-flex xs7>
          <v-checkbox
            hide-details
            class="mt-0"
            label="Save to dataset"
            v-model="preserve"
          ></v-checkbox>
        </v-flex>
        <v-flex xs4 offset-xs1>
          <v-btn block depressed color='primary' class='' @click="apply">
            Apply
            <v-icon class='ml-1'>check</v-icon>
          </v-btn>
        </v-flex>
      </v-layout>
    </v-container>
  </div>
</template>

<script>
import Stroke from "./Stroke";
import Fill from "./Fill";
import cloneDeep from "lodash-es/cloneDeep";

export default {
  name: "VectorDatasetVisualizationPane",
  components: { Stroke, Fill },
  props: {
    dataset: {
      type: Object,
      required: true
    },
    summary: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      enabled: true,
      preserve: false,
      currentTab: null,
      vizProperties: cloneDeep(this.dataset.meta.vizProperties)
    };
  },
  created() {
    this.currentTab = this.summary.types.pointAlike
      ? 0
      : this.summary.types.lineAlike ? 1 : 2;
  },
  methods: {
    apply() {
      // this.$set(
      //   this.dataset.meta,
      //   "vizProperties",
      //   cloneDeep(this.vizProperties)
      // );
      this.dataset.meta.vizProperties = cloneDeep(this.vizProperties);
    }
  }
};
</script>

<style lang="scss">
</style>
