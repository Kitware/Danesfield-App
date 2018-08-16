<template>
  <transition name="fade" mode="out-in">
    <div v-if='!editingWorkingSet'>
      <v-expansion-panel>
        <v-expansion-panel-content
          v-for="workingSet in workingSets"
          :key="workingSet._id">
          <div slot='header'>{{workingSet.name}}</div>
            <v-layout>
              <v-flex xs2 offset-xs1>
                <v-btn block color='grey lighten-4' depressed @click="$store.commit('workingSet/setEditingWorkingSet',workingSet)">
                  <v-icon>edit</v-icon>
                </v-btn>
              </v-flex>
              <v-flex xs4 offset-xs4>
                <v-btn block color='primary' depressed @click="focusWorkingSet(workingSet)">
                  Focus
                  <v-icon class='pl-1'>center_focus_strong</v-icon>
                </v-btn>
              </v-flex>
            </v-layout>
        </v-expansion-panel-content>
      </v-expansion-panel>
      <NewWithName name="working set" default='working-set-1' @confirm='addNewWorkingSet' />
    </div>
    <EditWorkingSet v-else />
  </transition>
</template>

<style lang="scss" scoped>
</style>

<script>
import { mapState, mapMutations } from "vuex";

import EditWorkingSet from "../components/EditWorkingSet";
import NewWithName from "../components/NewWithName";

export default {
  name: "WorkingSetModule",
  components: {
    NewWithName,
    EditWorkingSet
  },
  data() {
    return {};
  },
  computed: {
    ...mapState(["workingSets"]),
    ...mapState("workingSet", ["editingWorkingSet"])
  },
  watch: {},
  created() {},
  methods: {
    addNewWorkingSet(name) {
      var workingSet = { name, filter: null, datasetIds: [] };
      this.setEditingWorkingSet(workingSet);
    },
    focusWorkingSet(workingSet) {
      this.$store.commit("setSelectWorkingSetId", workingSet._id);
      this.$router.push("focus");
    },
    ...mapMutations("workingSet", ["setEditingWorkingSet"])
  }
};
</script>
