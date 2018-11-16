/*#############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
#############################################################################*/

<template>
  <transition name="fade" mode="out-in">
    <div v-if='!editingWorkingSet' class="workingset-module">
      <NewWithName name="working set" no-confirm @confirm='addNewWorkingSet' />
      <v-list class="workingsets">
        <template
          v-for="node in workingSetsTree">
          <WorkingSetListTile
            :key="node.workingSet._id"
            v-if="!node.children.length"
            :workingSet="node.workingSet"
            @focusWorkingSet="focusWorkingSet($event)"
            @setEditingWorkingSet="setEditingWorkingSet($event)" />
          <v-list-group
            v-else
            :key="node.workingSet._id">
              <WorkingSetListTile
                slot="activator"
                :workingSet="node.workingSet"
                @focusWorkingSet="focusWorkingSet($event)"
                @setEditingWorkingSet="setEditingWorkingSet($event)" />
              <WorkingSetListTile
                v-for="node in node.children"
                :key="node.workingSet._id"
                :workingSet="node.workingSet"
                class="result-workingset"
                @focusWorkingSet="focusWorkingSet($event)"
                @setEditingWorkingSet="setEditingWorkingSet($event)" />
          </v-list-group>
        </template>
      </v-list>
    </div>
    <EditWorkingSet v-else />
  </transition>
</template>

<script>
import { mapState, mapMutations, mapGetters } from "vuex";
import NewWithName from "resonantgeoview/src/components/NewWithName";

import EditWorkingSet from "../components/EditWorkingSet";
import WorkingSetListTile from "./WorkingSetListTile";

export default {
  name: "WorkingSetModule",
  components: {
    NewWithName,
    EditWorkingSet,
    WorkingSetListTile
  },
  data() {
    return {};
  },
  computed: {
    ...mapState("workingSet", ["editingWorkingSet"]),
    ...mapGetters(["workingSetsTree", "flattenedWorkingSets"])
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

.result-workingset {
  padding-left: 10px;
}
</style>

<style lang="scss">
.workingset-module {
  .workingsets {
    .v-list__group__header {
      .v-list__tile {
        padding-right: 6px;
      }

      .v-list__group__header__append-icon {
        padding-left: 4px;
      }
    }

    .v-list__tile .v-list__tile__action {
      min-width: 32px;
    }
  }
}
</style>
