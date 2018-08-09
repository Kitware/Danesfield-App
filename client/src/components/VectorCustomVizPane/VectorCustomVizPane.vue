<template>
  <div class="vector-customize-viz-pane">
    <v-tabs
      grow
      v-model="currentTab"
      color="white">
      <v-tab key="point" :disabled="!summary.types.pointAlike">POINTS</v-tab>
      <v-tab key="line" :disabled="!summary.types.lineAlike">LINES</v-tab>
      <v-tab key="polygon" :disabled="!summary.types.polygonAlike">POLYGONS</v-tab>
      <v-tab-item key="point">
        <Stroke :enabled.sync="vizProperties.point.stroke"
          :property.sync="vizProperties.point.strokeProperty"
          :properties="summary.properties"
          :color.sync="vizProperties.point.strokeColor"
          :scheme.sync="vizProperties.point.strokeScheme"
          :opacity.sync="vizProperties.point.strokeOpacity"
          :width.sync="vizProperties.point.strokeWidth" />
        <Fill :enabled.sync="vizProperties.point.fill"
          :property.sync="vizProperties.point.fillProperty"
          :properties="summary.properties"
          :color.sync="vizProperties.point.fillColor"
          :scheme.sync="vizProperties.point.fillScheme"
          :opacity.sync="vizProperties.point.fillOpacity"
          :scale.sync="vizProperties.point.fillScale"
          :radius.sync="vizProperties.point.radius" />
      </v-tab-item>
      <v-tab-item key="line">
        <Stroke :enabled.sync="vizProperties.line.stroke"
          :property.sync="vizProperties.line.strokeProperty"
          :properties="summary.properties"
          :color.sync="vizProperties.line.strokeColor"
          :scheme.sync="vizProperties.line.strokeScheme"
          :opacity.sync="vizProperties.line.strokeOpacity"
          :width.sync="vizProperties.line.strokeWidth" />
      </v-tab-item>
      <v-tab-item key="polygon">
        <Stroke :enabled.sync="vizProperties.polygon.stroke"
          :property.sync="vizProperties.polygon.strokeProperty"
          :properties="summary.properties"
          :color.sync="vizProperties.polygon.strokeColor"
          :scheme.sync="vizProperties.polygon.strokeScheme"
          :opacity.sync="vizProperties.polygon.strokeOpacity"
          :width.sync="vizProperties.polygon.strokeWidth" />
        <Fill :enabled.sync="vizProperties.polygon.fill"
          :property.sync="vizProperties.polygon.fillProperty"
          :properties="summary.properties"
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
            :input-value="preserve"
            @change="$emit('update:preserve',$event)"
          ></v-checkbox>
        </v-flex>
        <v-flex xs4 offset-xs1>
          <v-btn block outline color='primary' class='' @click="revert">
            Revert
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
import debounce from "lodash-es/debounce";

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
    },
    preserve: {
      type: Boolean,
      default: null
    }
  },
  data() {
    return {
      currentTab: null,
      initialVizProperties: cloneDeep(this.dataset.meta.vizProperties),
      vizProperties: cloneDeep(this.dataset.meta.vizProperties)
    };
  },
  watch: {
    vizProperties: {
      handler() {
        this.debouncedApply();
      },
      deep: true
    }
  },
  created() {
    this.currentTab = this.summary.types.pointAlike
      ? 0
      : this.summary.types.lineAlike ? 1 : 2;
    this.debouncedApply = debounce(this.apply, 200);
  },
  methods: {
    apply() {
      this.dataset.meta.vizProperties = cloneDeep(this.vizProperties);
    },
    revert() {
      this.dataset.meta.vizProperties = cloneDeep(this.initialVizProperties);
      this.vizProperties = cloneDeep(this.initialVizProperties);
    }
  }
};
</script>

<style lang="scss">
</style>
