<template>
  <v-select
    :items="items"
    hide-details
    placeholder=" "
    dense
    label="Color"
    :value="scheme"
    @input="$emit('update:scheme', $event)">
    <template slot="item" slot-scope="data">
      <div class="d-flex scheme item">
        <div class="flex1" v-for="color of toSchemeColors(data.item)" :key='color' :style="{background:color}">
        </div>
      </div>
    </template>
    <template slot="selection" slot-scope="data">
      <div class="d-flex scheme">
        <div class="flex1" v-for="color of toSchemeColors(data.item)" :key='color' :style="{background:color}">
        </div>
      </div>
    </template>
  </v-select>
</template>

<script>
import {
  colorbrewerCategories,
  toSchemeColors
} from "../../utils/palettableColorbrewerMapper";

export default {
  name: "ColorbrewerPicker",
  props: {
    scheme: {
      type: String
    }
  },
  data() {
    return {
      toSchemeColors
    };
  },
  computed: {
    items() {
      var items = [];
      if (this.scheme) {
        items = [this.scheme, { divider: true }];
      }
      for (let category of Object.keys(colorbrewerCategories)) {
        items.push({ header: category });
        items = [...items, ...colorbrewerCategories[category]];
      }
      return items;
    }
  }
};
</script>

<style lang="scss" scoped>
.scheme {
  height: 20px;
  width: 100%;

  &.item {
    min-width: 140px;
  }
}
</style>
