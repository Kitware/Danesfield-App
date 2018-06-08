<template>
  <div class="workspace-container">
    <transition-group class="views" name="view" tag="div">
      <div class='view' :key=key v-for="(value, key) in $slots" v-if="(!maximizeSlotName || maximizeSlotName===key) && !key.endsWith('actions')">
        <Workspace 
          :maximized="maximizeSlotName===key"
          @maximize="maximizeSlotName=key"
          @minimize="maximizeSlotName=null"
          :focused="focus===key"
          @focus="$emit('update:focus', key)"
          @duplicate="$emit('duplicate', key)"
          @close="$emit('close', key)">
          <slot :name="key"></slot>
          <slot :name="key+'-actions'" slot='actions'></slot>
        </Workspace>
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
      type: String,
      default: null
    }
  },
  data() {
    return {
      maximizeSlotName: null
    };
  },
  computed: {},
  watch: {},
  created() {
    window.container=this;
  },
  beforeUpdate() {},
  methods: {}
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
      transition: all 0.15s;
      background: #ddd;

      // .view-enter-active {
      //   transition: all 10s ease;
      // }
      // .view-leave-active {
      //   transition: all 10s ease;
      // }
      &.view-leave-to/*, .view-enter*/ {
        flex-grow: 0.00001;
      }
    }
  }
}
</style>
