<template>
<v-layout>
  <v-flex>
    <v-menu
    ref="menu"
    :close-on-content-click="false"
    :nudge-right="40"
    :return-value='localStart'
    lazy
    full-width
    offset-y
    min-width="290px"
    >
      <v-text-field
          slot="activator"
          v-model="localStart"
          label="Start date"
          prepend-icon="event"
          readonly
      ></v-text-field>
      <v-date-picker v-model="localStart" @input="$refs.menu.save(localStart)" no-title scrollable>
      </v-date-picker>
    </v-menu>
  </v-flex>
  <v-flex>
    <v-menu
    ref="menu2"
    :close-on-content-click="false"
    :nudge-right="40"
    :return-value='localEnd'
    lazy
    full-width
    offset-y
    min-width="290px"
    >
      <v-text-field
          slot="activator"
          v-model="localEnd"
          label="End date"
          prepend-icon="event"
          readonly
      ></v-text-field>
      <v-date-picker v-model="localEnd" @input="$refs.menu2.save(localEnd)" no-title scrollable>
      </v-date-picker>
    </v-menu>
  </v-flex>
</v-layout>
</template>

<style lang="scss" scoped>
</style>

<script>
export default {
  name: "DateRangeControl",
  props: {
    start: {
      type: String,
      default: null
    },
    end: {
      type: String,
      default: null
    }
  },
  data() {
    return {
      localStart: this.start ? this.start : null,
      localEnd: this.end ? this.end : null
    };
  },
  computed: {},
  watch: {
    start(value) {
      this.localStart = value ? value : null;
    },
    end(value) {
      this.localEnd = value ? value : null;
    },
    localStart(date) {
      this.$emit("update:start", date);
    },
    localEnd(date) {
      this.$emit("update:end", date);
    }
  },
  methods: {
  }
};
</script>
