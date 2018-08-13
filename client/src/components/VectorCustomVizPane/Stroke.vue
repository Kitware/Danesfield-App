<template>
<StyleSection title="Stroke" :enabled="enabled" @update:enabled="$emit('update:enabled',$event)">
  <v-container fluid grid-list-xl class="px-3">
    <v-layout align-center>
      <v-flex>
        <v-slider class=""
          :disabled="!enabled"
          hide-details
          thumb-label
          :min="0"
          :max="4"
          :step="0.05"
          label="Width"
          :value='width'
          @input="$emit('update:width',$event)"></v-slider>
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
  </v-container>
</StyleSection>
</template>

<script>
import ColorbrewerPicker from "./ColorbrewerPicker";
import BasicColorPicker from "./BasicColorPicker";
import StyleSection from "./StyleSection";
import { colorbrewerCategories } from "../../utils/palettableColorbrewerMapper";

export default {
  name: "Stroke",
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
    width: {
      type: Number,
      required: true
    },
    opacity: {
      type: Number,
      required: true
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
      } else {
        this.$emit("update:scheme", null);
      }
    }
  }
};
</script>

<style>
</style>
