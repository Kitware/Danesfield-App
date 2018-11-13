/*#############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
#############################################################################*/

<template>
  <transition name="fade" mode="out-in">
    <div v-if='!editingWorkingSet'>
      <NewWithName name="working set" no-confirm @confirm='addNewWorkingSet' />
      <v-expansion-panel>
        <v-expansion-panel-content
          v-for="flattened in flattenedWorkingSets"
          :key="flattened.workingSet._id"
          :style="{paddingLeft:Math.min(12*flattened.level,50)+'px'}"
          :class="{child:flattened.level}">
          <div slot='header'>{{flattened.workingSet.name.split(': ').slice(-1)[0]}}</div>
            <v-layout>
              <v-flex xs2 offset-xs1>
                <v-btn block color='grey lighten-4' depressed @click="$store.commit('workingSet/setEditingWorkingSet',flattened.workingSet)">
                  <v-icon>edit</v-icon>
                </v-btn>
              </v-flex>
              <v-flex xs4 offset-xs4>
                <v-btn block color='primary' depressed @click="focusWorkingSet(flattened.workingSet)">
                  Focus
                  <v-icon class='pl-1'>center_focus_strong</v-icon>
                </v-btn>
              </v-flex>
            </v-layout>
        </v-expansion-panel-content>
      </v-expansion-panel>
    </div>
    <EditWorkingSet v-else />
  </transition>
</template>

<script>
import { mapState, mapMutations, mapGetters } from "vuex";

import EditWorkingSet from "../components/EditWorkingSet";
import NewWithName from "resonantgeoview/src/components/NewWithName";

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
    ...mapState("workingSet", ["editingWorkingSet"]),
    ...mapGetters(["flattenedWorkingSets"])
  },
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

<style lang="scss" scoped>
.theme--light.v-expansion-panel .v-expansion-panel__container.child {
  background-color: #f5f5f5;
}
</style>
