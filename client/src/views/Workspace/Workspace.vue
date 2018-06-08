<template>
  <div class='workspace' @click="focus">
    <div class='focus-indicator' v-if='focused'></div>
    <div class='button-container'>
      <v-menu offset-y>
        <v-btn slot="activator" 
          small
          outline
          color="primary"
        ><v-icon>menu</v-icon></v-btn>
        <v-list>
          <v-list-tile @click="$emit('duplicate')">
            <v-list-tile-title>Duplicate</v-list-tile-title>
          </v-list-tile>
          <v-list-tile @click="$emit('close')">
            <v-list-tile-title>Close</v-list-tile-title>
          </v-list-tile>
          <v-divider v-if='$slots.actions'></v-divider>
          <slot name='actions'></slot>
        </v-list>
      </v-menu>
      <v-btn
        small
        outline
        color="primary"
        @click="$emit(maximized?'minimize':'maximize')"
      >
        <v-icon v-if="!maximized">maximize</v-icon>
        <v-icon v-if="maximized">minimize</v-icon>
      </v-btn>
    </div>
    <slot></slot>
  </div>
</template>

<script>
export default {
  name: "Workspace",
  props: {
    maximized: {
      type: Boolean,
      default: false
    },
    focused: Boolean
  },
  data() {
    return {};
  },
  computed: {},
  created() {},
  methods: {
    focus() {
      this.$emit("focus");
    }
  }
};
</script>

<style lang="scss" scoped>
.workspace {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;

  .focus-indicator {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background-color: #2196f3;
    z-index: 1;
  }

  .button-container {
    position: absolute;
    top: 0;
    right: 0;
    z-index: 1;
  }
}
</style>

<style lang="scss">
.workspace .btn__content {
  padding: 0 2px;
}
</style>
