<template>
  <div class='new-workingset'>
    <transition name="fade" mode='out-in'>
      <v-btn flat block large 
      class='my-0 button'
      v-if="!adding"
      color='primary'
      @click="adding = true">
        <v-icon class='mr-2'>add_circle</v-icon>
        New working set
      </v-btn>
      <v-text-field
        class="input"
        v-if="adding"
        name="Name"
        label="Name"
        v-model="value"
        hide-details
        :light='true'
        append-icon='add_circle'
        :append-icon-cb='confirm'
        prepend-icon='cancel'
        :prepend-icon-cb='()=>{adding=false}'
      ></v-text-field>
    </transition>
  </div>
</template>

<style lang="scss" scoped>
.new-workingset {
  height: 50px;
  position: relative;
}

.button {
  height: 100%;
}

.button,
.input {
  position: absolute;
}
</style>

<script>
export default {
  name: "NewWorkingSet",
  props: {
    default: {
      type: String,
      default: ""
    }
  },
  data() {
    return {
      adding: false,
      value: this.default
    };
  },
  methods: {
    confirm() {
      this.adding = false;
      this.$emit("confirm", this.value);
    }
  }
};
</script>
