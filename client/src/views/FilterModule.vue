<template>
  <transition name="fade" mode="out-in">
    <div v-if='!editingFilter'>
      <v-expansion-panel>
        <v-expansion-panel-content
          v-for="filter in filters" 
          :key="filter._id">
          <div slot='header'>{{filter.name}}</div>
          <v-container grid-list-xs>
            <v-layout row wrap>
              <v-flex xs2 offset-xs1>
                <v-btn block color='grey lighten-3' depressed @click="setEditingFilter(filter)">
                  <v-icon>edit</v-icon>
                </v-btn>
              </v-flex>
              <v-flex xs7 offset-xs1>
                <v-btn block color='primary' class='' depressed @click="$store.commit('createWorkingSetFromFilter',filter)">
                  Create Working set
                </v-btn>
              </v-flex>
            </v-layout>
          </v-container>
        </v-expansion-panel-content>
      </v-expansion-panel>
      <NewWithName name="filter" default="filter-1" @confirm='addNewFilter' />
    </div>
    <EditFilter v-else />
  </transition>
</template>

<style lang="scss" scoped>
</style>

<script>
import { mapState, mapMutations } from "vuex";

import NewWithName from "../components/NewWithName";
import EditFilter from "../components/EditFilter";

export default {
  name: "FilterModule",
  components: {
    NewWithName,
    EditFilter
  },
  props: {
    // start: {
    //   type: String,
    //   default: null
    // },
    // end: {
    //   type: String,
    //   default: null
    // }
  },
  data() {
    return {};
  },
  computed: {
    ...mapState(["filters"]),
    ...mapState("filter", ["editingFilter"])
  },
  watch: {},
  created() {
  },
  methods: {
    addNewFilter(name) {
      var filter = { name, conditions: [] };
      this.setEditingFilter(filter);
    },
    ...mapMutations("filter", ["setEditingFilter"])
  }
};
</script>
