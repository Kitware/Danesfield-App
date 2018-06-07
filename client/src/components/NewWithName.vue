<template>
  <v-container grid-list-md class='new-with-name py-0'>
    <v-layout row wrap>
      <v-flex>
        <transition name="fade" mode='out-in'>
          <v-btn flat block large
          v-if="!adding"
          color='primary'
          @click="adding = true">
            <v-icon class='mr-2'>add_circle</v-icon>
            New {{name}}
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
      </v-flex>
    </v-layout>
  </v-container>
</template>

<style lang="scss" scoped>
.new-with-name {
  position: relative;
}
</style>

<script>
export default {
  name: "NewWithName",
  props: {
    name: String,
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
