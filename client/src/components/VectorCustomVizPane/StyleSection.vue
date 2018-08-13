<template>
  <v-list class="py-0 style-section">
  <v-list-group :value="true">
    <v-list-tile slot="activator">
      <v-list-tile-action class="narrow-list-tile-action" @click.stop>
        <v-checkbox
          color="white"
          dark
          :input-value="enabled"
          @change="$emit('update:enabled',$event)"></v-checkbox>
      </v-list-tile-action>
      <v-list-tile-content>
        <v-list-tile-title>{{title}}</v-list-tile-title>
      </v-list-tile-content>
    </v-list-tile>
    <slot></slot>
  </v-list-group>
</v-list>
</template>

<script>
export default {
  name: "StyleSection",
  props: {
    title: {
      type: String,
      required: true
    },
    enabled: {
      type: Boolean,
      required: true
    }
  }
};
</script>

<style lang="scss">
.style-section.v-list .v-list__group__header {
  background-color: #444;
  color: white;

  &:hover {
    background-color: #555;
  }

  .v-list__group__header__append-icon .v-icon {
    color: inherit;
  }
}
</style>
