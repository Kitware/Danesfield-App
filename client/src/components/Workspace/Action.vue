<template>
<v-list-tile :disabled="disabled" @click="$listeners.click">
  <v-list-tile-title><slot></slot></v-list-tile-title>
</v-list-tile>
</template>

<script>
export default {
  props: {
    disabled: {
      type: Boolean,
      default: false
    }
  }
};
</script>
