<template>
  <div class='workspace' @click="focus">
    <div class='focus-indicator' v-if='!onlyWorkspace && focused'></div>
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
          <v-list-tile :disabled="onlyWorkspace" @click="close">
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
        @click="sendEvent()"
        v-if="!onlyWorkspace"
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
  inject: ["container"],
  props: {
    identifier: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      maximized: false,
      focused: false,
      onlyWorkspace: false
    };
  },
  computed: {
    bar() {
      return this.foo;
    }
  },
  created() {
    // console.log("workspace created");
    this.container.$on("workspaceMaximized", this.workspaceMaximized);
    this.container.$on("workspacesChanged", this.workspacesChanged);
    this.container.$on("update:focus", this.focusChanged);
    this.workspacesChanged(this.container.workspaces);
  },
  beforeDestroy() {
    this.container.$off("workspaceMaximized", this.workspaceMaximized);
    this.container.$off("workspacesChanged", this.workspacesChanged);
    this.container.$off("update:focus", this.focusChanged);
  },
  watch: {},
  methods: {
    focus() {
      this.container.$emit("workspace_focus", this.identifier);
    },
    sendEvent() {
      this.container.$emit(
        this.maximized ? "workspace_minimize" : "workspace_maximize",
        this.identifier
      );
    },
    close() {
      if (!this.onlyWorkspace) {
        this.$emit("close");
      }
    },
    workspaceMaximized(identifier) {
      this.maximized = identifier === this.identifier;
    },
    focusChanged(identifier) {
      this.focused = identifier === this.identifier;
    },
    workspacesChanged(workspaces) {
      this.onlyWorkspace = workspaces.length === 1;
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
