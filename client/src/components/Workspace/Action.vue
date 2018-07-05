<template>
<v-list-tile @click="$listeners.click">
  <v-list-tile-title><slot></slot></v-list-tile-title>
</v-list-tile>
</template>

<script>
export default {
  props: {
  }
};
</script>

<style lang="scss">
</style>
