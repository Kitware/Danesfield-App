<template>
  <div class='workspace' @mousedown="focus">
    <div class='focus-indicator' v-if='!onlyWorkspace && focused'></div>
    <div class='button-container'>
      <v-menu offset-y>
        <v-btn slot="activator" 
          small
          flat
          color="primary"
        ><v-icon>more_vert</v-icon></v-btn>
        <v-list>
          <v-list-tile
            v-if="$listeners.split"
            :disabled="workspaces.length===max" 
            @click="split">
            <v-list-tile-title>Split</v-list-tile-title>
          </v-list-tile>
          <v-list-tile
            v-if="$listeners.close"
            :disabled="onlyWorkspace" 
            @click="close">
            <v-list-tile-title>Close</v-list-tile-title>
          </v-list-tile>
          <v-divider v-if='$slots.actions && ($listeners.split || $listeners.close)'></v-divider>
          <slot name='actions'></slot>
        </v-list>
      </v-menu>
      <v-btn
        small
        flat
        color="primary"
        @click="sendEvent()"
        v-if="!onlyWorkspace"
        :title="!maximized?'Maximize':'Minimize'"
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
      type: [String, Number, Object],
      required: true
    }
  },
  data() {
    return {
      maximizedWorkspace: null,
      focusedWorkspace: null,
      workspaces: null,
      max: null
    };
  },
  computed: {
    maximized() {
      return this.maximizedWorkspace === this.identifier;
    },
    onlyWorkspace() {
      return this.workspaces.length === 1;
    },
    focused() {
      return this.focusedWorkspace === this.identifier;
    }
  },
  created() {
    this.container.$on("workspaceMaximized", this.workspaceMaximized);
    this.container.$on("workspacesChanged", this.workspacesChanged);
    this.workspacesChanged(this.container.workspaces);
    this.container.$on("update:focused", this.focusChanged);
    this.focusChanged(this.container.focused);
    this.container.$on("maxChanged", this.maxChanged);
    this.maxChanged(this.container.max);
  },
  beforeDestroy() {
    this.container.$off("workspaceMaximized", this.workspaceMaximized);
    this.container.$off("workspacesChanged", this.workspacesChanged);
    this.container.$off("update:focused", this.focusChanged);
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
    split() {
      if (this.workspaces.length !== this.max) {
        this.$emit("split");
      }
    },
    close() {
      if (!this.onlyWorkspace) {
        this.$emit("close");
      }
    },
    workspaceMaximized(identifier) {
      this.maximizedWorkspace = identifier;
    },
    focusChanged(identifier) {
      this.focusedWorkspace = identifier;
    },
    workspacesChanged(workspaces) {
      this.workspaces = workspaces;
    },
    maxChanged(max) {
      this.max = max;
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
