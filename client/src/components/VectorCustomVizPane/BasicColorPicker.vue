<template>
  <v-select
    :items="items"
    hide-details
    placeholder=" "
    dense
    label="Color"
    :value="color"
    @input="$emit('update:color', $event)">
    <template slot="item" slot-scope="data">
      <div class="color" :style="{background:data.item}"></div>
    </template>
    <template slot="selection" slot-scope="data">
      <div class="color" :style="{background:data.item}"></div>
    </template>
  </v-select>
</template>

<script>
export default {
  name: "BasicColorPicker",
  props: {
    color: {
      type: String,
      required: true
    }
  },
  data() {
    return {};
  },
  computed: {
    items() {
      var items = [];
      if (this.color) {
        items = [this.color, { divider: true }];
      }
      items = [
        ...items,
        ...[
          "#a6cee3",
          "#000000",
          "#1f78b4",
          "#b2df8a",
          "#33a02c",
          "#fb9a99",
          "#e31a1c",
          "#fdbf6f",
          "#ff7f00",
          "#cab2d6",
          "#6a3d9a",
          "#ffff99",
          "#b15928"
        ]
      ];
      return items;
    }
  }
};
</script>

<style lang="scss" scoped>
.color {
  height: 18px;
  width: 100%;
  border: 1px solid #333;
}
</style>
