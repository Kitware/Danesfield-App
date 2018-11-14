/*#############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
#############################################################################*/

<template>
<div class="palette">
  <div
    v-for="color in colors"
    :key="color"
    class="item"
  >
    <div
      class="blot"
      :style="{
        width: `${size}px`,
        height: `${size}px`,
        background: color,
      }"
      v-on:click="$emit('input', color)"
    >
      <v-icon
        v-if="color === value"
        class="check"
        :size="size"
      >
        check
      </v-icon>
    </div>
  </div>
</div>
</template>

<script>
import colors from "./paletteColors";

export default {
  name: "Palette",
  props: {
    size: {
      type: Number,
      default: 24
    },
    value: {
      type: String,
      default: ""
    }
  },
  data() {
    return {
      colors
    };
  },
  methods: {
    getStyles(color) {
      return {
        width: `${this.size}px`,
        height: `${this.size}px`,
        background: color
      };
    }
  }
};
</script>

<style lang="scss" scoped>
.palette {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
}

.item {
  position: relative;
}

.blot {
  position: relative;
  box-shadow: inset 0 0 0 1px rgba(0, 0, 0, 0.3);
  border-radius: 25%;
  margin: 4px;
  cursor: pointer;
  transition: border 50ms;

  &:hover {
    border: 1px solid rgba(0, 0, 0, 0.8);
  }
}

.check {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate3d(-50%, -50%, 0);
  pointer-events: none;
  color: white !important;
  mix-blend-mode: exclusion;
}
</style>
