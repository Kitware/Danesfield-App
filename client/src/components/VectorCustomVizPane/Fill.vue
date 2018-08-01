<template>
<StyleSection title="Fill" :enabled="enabled" @update:enabled="$emit('update:enabled',$event)">
  <v-container fluid grid-list-xl class="px-3">
    <v-layout align-center>
      <v-flex xs6>
        <v-select
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
        <BasicColorPicker v-if="!property" :color="color" @update:color="$emit('update:color', $event)" />
        <ColorbrewerPicker v-else :scheme="scheme" @update:scheme="$emit('update:scheme', $event)" />
      </v-flex>
    </v-layout>
    <v-layout align-center>
      <v-flex>
        <v-slider class=""
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
      type: Array,
      required: true
    },
    scheme: {
      type: String
    },
    opacity: {
      type: Number,
      required: true
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
        ...this.properties.map(property => ({
          name: property,
          value: property
        }))
      ];
    }
  }
};
</script>

<style>
</style>
