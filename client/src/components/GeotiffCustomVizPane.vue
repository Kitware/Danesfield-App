<template>
  <v-container fluid grid-list-md class="py-2 geotiff-customize-viz-pane">
    <v-layout>
      <v-flex>
        <v-radio-group
          hide-details
          v-model="mode">
          <v-radio label="Default" value="default"></v-radio>
          <v-radio label="Custom" value="custom"></v-radio>
        </v-radio-group>
      </v-flex>
    </v-layout>
    <v-layout>
    </v-layout>
    <template v-if="vizProperties">
      <v-layout>
        <v-flex xs5>
          <v-select
            :items="bands"
            hide-details
            label="Band"
            placeholder=" "
            v-model="vizProperties.band" />
        </v-flex>
      </v-layout>
      <v-layout>
        <v-flex xs6>
          <ColorbrewerPicker
            :scheme.sync="vizProperties.scheme" />
        </v-flex>
        <v-flex xs6>
          <v-select
            :items="[{name:'Continuous',value:'linear'},{name:'Discrete',value:'discrete'}]"
            item-text="name"
            item-value="value"
            hide-details
            label="Type"
            placeholder=" "
            v-model="vizProperties.type" />
        </v-flex>
      </v-layout>
      <v-layout class="mt-2">
        <v-flex xs6>
          <v-text-field
            v-model="vizProperties.range[0]"
            label="Min"
            hide-details
            type="number"
          ></v-text-field>
        </v-flex>
        <v-flex xs6>
          <v-text-field
            v-model="vizProperties.range[1]"
            label="Max"
            hide-details
            type="number"
          ></v-text-field>
        </v-flex>
      </v-layout>
      <v-layout class="mt-3">
        <v-flex>
          <v-range-slider
          v-model="vizProperties.range"
          :max="max"
          :min="min"
          :step="1"
        ></v-range-slider>
        </v-flex>
      </v-layout>
    </template>
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
</template>

<script>
import cloneDeep from "lodash-es/cloneDeep";
import debounce from "lodash-es/debounce";

import ColorbrewerPicker from "./VectorCustomVizPane/ColorbrewerPicker";
import { colorbrewerCategories } from "../utils/palettableColorbrewerMapper";

export default {
  name: "GeotiffCustomVizPane",
  components: { ColorbrewerPicker },
  props: {
    dataset: {
      type: Object,
      required: true
    },
    meta: {
      type: Object,
      required: true
    },
    preserve: {
      type: Boolean,
      default: null
    }
  },
  computed: {
    bands() {
      return Object.keys(this.meta.bands);
    },
    max() {
      var band = this.vizProperties.band;
      if (!band) {
        return null;
      } else {
        return parseInt(this.meta.bands[band].max.toFixed(0));
      }
    },
    min() {
      var band = this.vizProperties.band;
      if (!band) {
        return null;
      } else {
        return parseInt(this.meta.bands[band].min.toFixed(0));
      }
    },
    mode: {
      get() {
        return this.vizProperties ? "custom" : "default";
      },
      set(newValue) {
        switch (newValue) {
          case "default":
            this.vizProperties = null;
            break;
          case "custom":
            var band = this.bands[0];
            this.vizProperties = {
              band: this.bands[0],
              scheme:
                colorbrewerCategories[Object.keys(colorbrewerCategories)[0]][0],
              type: "linear",
              range: null
            };
            this.vizProperties.range = [this.min, this.max];
            break;
        }
      }
    }
  },
  data() {
    return {
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
    this.debouncedApply = debounce(this.apply, 200);
  },
  methods: {
    apply() {
      this.$set(
        this.dataset.meta,
        "vizProperties",
        cloneDeep(this.vizProperties)
      );
    },
    revert() {
      this.vizProperties = cloneDeep(this.initialVizProperties);
    }
  }
};
</script>

<style>
</style>
