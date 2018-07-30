<template>
<v-btn icon @click="look" ref="button">
  <slot></slot>
</v-btn>
</template>

<script>
export default {
  name: "WorkspaceAction",
  props: {
    disabled: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    look(e) {
      if (
        e.target !== this.$refs.button.$el &&
        e.target !== this.$refs.button.$el.firstChild
      ) {
        return;
      }
      var innerActivator = this.$refs.button.$el.querySelector(
        "[class$='__activator']"
      );
      if (innerActivator) {
        innerActivator.click();
      }
    }
  }
};
</script>
