<template>
<StyleSection title="Fill" :enabled="enabled" @update:enabled="$emit('update:enabled',$event)">
  <v-container fluid grid-list-xl class="px-3">
    <v-layout align-center v-if="radius">
      <v-flex>
        <v-slider class=""
          :disabled="!enabled"
          hide-details
          thumb-label
          :min="1"
          :max="15"
          label="Radius"
          :value='radius'
          @input="$emit('update:radius',$event)"
          :step="0.5"></v-slider>
      </v-flex>
    </v-layout>
    <v-layout align-center>
      <v-flex xs6>
        <v-select
          :disabled="!enabled"
          :items="propertyItems"
          item-text="name"
          item-value="value"
          hide-details
          label="Property"
          placeholder=" "
          :value="property"
          @input="$emit('update:property', $event)">
        </v-select>
      </v-flex>
      <v-flex xs6>
        <BasicColorPicker
          v-if="!property"
          :disabled="!enabled"
          :color="color"
          @update:color="$emit('update:color', $event)" />
        <ColorbrewerPicker
          v-else
          :disabled="!enabled"
          :scheme="scheme"
          @update:scheme="$emit('update:scheme', $event)" />
      </v-flex>
    </v-layout>
    <v-layout align-center>
      <v-flex>
        <v-slider
          :disabled="!enabled"
          hide-details
          thumb-label
          :min="0"
          :max="1"
          label="Opacity"
          :value='opacity'
          @input="$emit('update:opacity',$event)"
          :step="0.01"></v-slider>
      </v-flex>
    </v-layout>
    <v-layout v-if="property && !properties[property].values">
      <v-flex xs3 class="pt-3">
        <v-label>Scale</v-label>
      </v-flex>
      <v-flex>
        <v-radio-group
          :disabled="!enabled"
          :value="scale"
          @change="$emit('update:scale',$event)">
          <v-radio
            label="Linear"
            value="linear"
          ></v-radio>
          <v-radio
            label="Logarithmic"
            value="log"
          ></v-radio>
          <v-radio
            label="Quantile"
            value="quantile"
          ></v-radio>
        </v-radio-group>
      </v-flex>
    </v-layout>
  </v-container>
</StyleSection>
</template>

<script>
import ColorbrewerPicker from "./ColorbrewerPicker";
import BasicColorPicker from "./BasicColorPicker";
import StyleSection from "./StyleSection";
import { colorbrewerCategories } from "../../utils/palettableColorbrewerMapper";

export default {
  name: "Fill",
  components: { StyleSection, BasicColorPicker, ColorbrewerPicker },
  props: {
    enabled: {
      type: Boolean,
      required: true
    },
    color: {
      type: String,
      required: true
    },
    property: {
      type: String
    },
    properties: {
      type: Object,
      required: true
    },
    scheme: {
      type: String
    },
    opacity: {
      type: Number,
      required: true
    },
    radius: {
      type: Number
    },
    scale: {
      type: String
    }
  },
  computed: {
    propertyItems() {
      return [
        { name: "Constant", value: null },
        { divider: true },
        ...Object.keys(this.properties).map(property => ({
          name: property,
          value: property
        }))
      ];
    }
  },
  watch: {
    property(newValue) {
      if (newValue) {
        if (!this.scheme) {
          this.$emit(
            "update:scheme",
            colorbrewerCategories[Object.keys(colorbrewerCategories)[0]][0]
          );
        }
        if (!this.scale && !this.properties[newValue].values) {
          this.$emit("update:scale", "linear");
        }
      } else {
        this.$emit("update:scheme", null);
        this.$emit("update:scale", null);
      }
    }
  }
};
</script>

<style>
</style>
