<template>
  <div class='workspace' @mousedown="focus" @click="focus">
    <div class="slot-container">
      <slot></slot>
    </div>
    <div class="bottom-bar">
      <div class='focus-indicator' v-if='!onlyWorkspace && focused'></div>
      <v-toolbar dark>
        <v-select class="state-selector" v-if="states"
          :value="selectedState"
          @input="$emit('stateChange', $event)"
          :items="states"
          item-text="name"
          item-value='value'
        ></v-select>
        <v-spacer />
        <slot name="actions"></slot>
        <v-tooltip top v-if="!onlyWorkspace">
          <span>{{!maximized?'Maximize':'Minimize'}}</span>
          <v-btn
            slot="activator"
            icon
            @click="maximizeOrMinimize"
          >
            <v-icon v-if="!maximized">maximize</v-icon>
            <v-icon v-if="maximized">minimize</v-icon>
          </v-btn>
        </v-tooltip>
        <v-tooltip top>
          <span>Split view</span>
          <v-btn
            slot="activator"
            icon
            v-if="workspaces.length!==max"
            @click="split"
          >
            <v-icon>flip</v-icon>
          </v-btn>
        </v-tooltip>
        <v-tooltip top v-if="$listeners.close && !onlyWorkspace">
          <span>Close</span>
          <v-btn
            slot="activator"
            icon
            @click="close"
          >
            <v-icon>close</v-icon>
          </v-btn>
        </v-tooltip>
      </v-toolbar>
    </div>
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
    },
    states: Array
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
    },
    selectedState() {
      return this.states.filter(state => state.disabled)[0];
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
      if (!this.focused) {
        this.container.$emit("workspace_focus", this.identifier);
      }
    },
    maximizeOrMinimize() {
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
  display: flex;
  flex-direction: column;

  .bottom-bar {
    height: 45px;
    position: relative;

    .state-selector {
      max-width: 200px;
    }

    .focus-indicator {
      position: absolute;
      top: 1px;
      left: 1px;
      width: 9px;
      height: 9px;
      z-index: 1;
      background: linear-gradient(
        135deg,
        #fff,
        #fff 50%,
        hsla(0, 0%, 100%, 0) 51%
      );
    }
  }

  .slot-container {
    flex: 1;
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
.workspace {
  .btn__content {
    padding: 0 2px;
  }

  .bottom-bar .toolbar__content {
    height: 45px !important;
  }
}
</style>
