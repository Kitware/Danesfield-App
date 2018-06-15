<template>
  <div class="workspace-container">
    <transition-group class="views" name="view" tag="div" @after-enter="afterTransition('afterEnter')" @after-leave="afterTransition('afterLeave')"
    @before-enter="beforeTransition('beforeEnter')" @before-leave="beforeTransition('beforeLeave')">
      <div class='view' :key=key v-for="(value, key) in $slots" v-if="!maximizedWorkspace || value[0].componentOptions.propsData.identifier===maximizedWorkspace">
        <slot :name='key'></slot>
      </div>
    </transition-group>
  </div>
</template>

<script>
import Workspace from "./Workspace";

export default {
  name: "WorkspaceContainer",
  components: {
    Workspace
  },
  props: {
    focus: {
      type: Object,
      default: null
    },
    autoResize: {
      type: Boolean,
      default: false
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
      // console.log("workspaces changed", value);
      this.$emit("workspacesChanged", value);
      this.maximizedWorkspace = null;
    }
  },
  created() {
    // console.log("Container created");
    window.container = this;
    this.$on("workspace_maximize", identifier => {
      this.maximizedWorkspace = identifier;
    });
    this.$on("workspace_minimize", identifier => {
      this.maximizedWorkspace = null;
    });
    this.$on("workspace_focus", identifier => {
      this.$emit("update:focus", identifier);
    });
    if (process.env.NODE_ENV === "development") {
      var names = Object.keys(this.$slots);
      if (names.length === 1 && names[0] === "default") {
        // console.error("Workspace Container needs named slot as slot");
        throw new Error("Workspace Container needs named slot as slot");
      }
    }
  },
  // render(h) {
  //   console.log("Container render()");
  //   return h("div", { class: ["workspace-container"] }, [
  //     h(
  //       "div",
  //       { class: ["views"] },
  //       Object.entries(this.$slots).map(([name, slot]) => {
  //         // slot[0].data.props = { abc: 1 };
  //         slot[0].componentOptions.propsData["abc"] = 1;
  //         var a = h(
  //           "div",
  //           {
  //             class: "view",
  //             key: name,
  //             props: {
  //               myProp: "bar"
  //             }
  //           },
  //           slot
  //         );
  //         return a;
  //       })
  //     )
  //   ]);
  // },
  // mounted() {
  //   console.log("Container mounted");
  // this.listenToMaximize();
  // },
  // beforeUpdate() {
  //   console.log("Container beforeUpdate");
  // this.stopListener();
  // },
  updated() {
    // console.log("Container updated");
    let workspaces = Object.values(this.$slots).map(
      ([workspaceVNode]) => workspaceVNode.componentOptions.propsData.identifier
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
  methods: {
    beforeTransition(transitionType) {
      // console.log("beforeTransition");
      this.$emit("beforeTransition", transitionType);
      if (this.autoResize) {
        clearInterval(this.resizeEventHandle);
        this.resizeEventHandle = setInterval(() => {
          // console.log('sending resize');
          window.dispatchEvent(new Event("resize"));
        }, 30);
      }
    },
    afterTransition(transitionType) {
      // console.log("afterTransition");
      this.$emit("afterTransition", transitionType);
      if (this.autoResize || this.resizeEventHandle) {
        window.dispatchEvent(new Event("resize"));
        clearInterval(this.resizeEventHandle);
        this.resizeEventHandle = null;
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
      flex-grow: 0.00001;
    }
  }
}
</style>
