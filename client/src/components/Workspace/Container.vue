<script>
import Workspace from "./Workspace";

export default {
  name: "WorkspaceContainer",
  components: {
    Workspace
  },
  render(h) {
    return h("div", { class: ["workspace-container"] }, [
      h(
        "transition-group",
        {
          class: ["views"],
          props: {
            name: "view",
            tag: "div"
          },
          on: {
            "after-enter": () => {
              this.afterTransition("afterEnter");
            },
            "after-leave": () => {
              this.afterTransition("afterLeave");
            },
            "before-enter": () => {
              this.beforeTransition("beforeEnter");
            },
            "before-leave": () => {
              this.beforeTransition("beforeLeave");
            }
          }
        },
        this.$slots.default.map((workspaceVNode, i) => {
          var { identifier } = workspaceVNode.componentOptions.propsData;
          if (
            this.maximizedWorkspace === null ||
            identifier === this.maximizedWorkspace
          ) {
            return h(
              "div",
              {
                class: {
                  view: true
                },
                style: {
                  "flex-grow":
                    this.flexGrowFirst && i === 0 ? this.flexGrowFirst : 1
                },
                key: identifier.valueOf()
              },
              [workspaceVNode]
            );
          } else {
            return null;
          }
        })
      )
    ]);
  },
  props: {
    focused: {
      type: [String, Number, Object],
      default: null
    },
    autoResize: {
      type: Boolean,
      default: false
    },
    continuousResizeInterval: {
      type: Number,
      default: null
    },
    max: {
      type: Number,
      default: 4
    },
    flexGrowFirst: {
      type: Number,
      default: null
    }
  },
  data() {
    return {
      maximizedWorkspace: null,
      workspaces: []
    };
  },
  provide() {
    return {
      container: this
    };
  },
  watch: {
    maximizedWorkspace(value) {
      this.$emit("workspaceMaximized", value);
    },
    workspaces(value) {
      this.maximizedWorkspace = null;
      this.setDefaultFocus();
      this.$emit("workspacesChanged", value);
    },
    max(value) {
      this.$emit("maxChanged", value);
    }
  },
  created() {
    window.container = this;
    setTimeout(() => {
      this.setDefaultFocus();
    }, 0);
    this.$on("workspace_maximize", identifier => {
      this.maximizedWorkspace = identifier;
    });
    this.$on("workspace_minimize", identifier => {
      this.maximizedWorkspace = null;
    });
    this.$on("workspace_focus", identifier => {
      this.$emit("update:focused", identifier);
    });
    this.updateWorkspace();
  },
  updated() {
    this.updateWorkspace();
  },
  methods: {
    updateWorkspace() {
      let workspaces = this.$slots.default.map(
        workspaceVNode => workspaceVNode.componentOptions.propsData.identifier
      );
      for (let workspace of this.workspaces) {
        if (workspaces.indexOf(workspace) == -1) {
          var index = this.workspaces.indexOf(workspace);
          this.workspaces.splice(index, 1);
        }
      }
      for (let workspace of workspaces) {
        if (this.workspaces.indexOf(workspace) == -1) {
          this.workspaces.push(workspace);
        }
      }
    },
    beforeTransition(transitionType) {
      this.$emit("beforeTransition", transitionType);
      if (this.autoResize) {
        clearInterval(this.resizeEventHandle);
        if (this.continuousResizeInterval) {
          this.resizeEventHandle = setInterval(() => {
            window.dispatchEvent(new Event("resize"));
          }, this.continuousResizeInterval);
        }
      }
    },
    afterTransition(transitionType) {
      this.$emit("afterTransition", transitionType);
      if (this.autoResize || this.resizeEventHandle) {
        window.dispatchEvent(new Event("resize"));
        clearInterval(this.resizeEventHandle);
        this.resizeEventHandle = null;
      }
    },
    setDefaultFocus() {
      if (!this.focused || this.workspaces.indexOf(this.focused) === -1) {
        this.$emit(
          "update:focused",
          this.$slots.default[0].componentOptions.propsData.identifier
        );
      }
    }
  }
};
</script>

<style lang="scss" scoped>
.workspace-container {
  height: 100%;

  .views {
    display: flex;
    height: 100%;

    .view {
      flex-grow: 1;
      flex-shrink: 1;
      flex-basis: auto;
      position: relative;
      overflow: hidden;
      background: #ddd;
      overflow-x: hidden;
    }

    .view-enter-active,
    .view-leave-active {
      transition: all 0.15s;
    }
    .view-leave-to,
    .view-enter {
      flex-grow: 0.00001 !important;
    }
  }
}
</style>
