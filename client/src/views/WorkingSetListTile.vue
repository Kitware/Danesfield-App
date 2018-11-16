/*#############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
#############################################################################*/

<script>
export default {
  name: "WorkingSetListTile",
  props: {
    workingSet: {
      required: true,
      type: Object
    }
  },
  data() {
    return {};
  }
};
</script>

<template>
  <v-list-tile class="hover-show-parent">
    <v-list-tile-content>
      <v-list-tile-title>
        {{workingSet.name.split(': ').slice(-1)[0]}}
      </v-list-tile-title>
    </v-list-tile-content>
    <v-list-tile-action class="hover-show-child" @click.stop>
      <v-btn flat icon color="grey" @click="$emit('focusWorkingSet',workingSet)">
        <v-icon>filter_center_focus</v-icon>
      </v-btn>
    </v-list-tile-action>
    <v-list-tile-action class="hover-show-child" @click.stop>
      <v-menu>
        <v-btn slot="activator" flat icon color="grey">
          <v-icon>more_vert</v-icon>
        </v-btn>
        <v-list>
          <v-list-tile @click="$emit('setEditingWorkingSet',workingSet)">
            <v-list-tile-title>Edit</v-list-tile-title>
          </v-list-tile>
          <v-list-tile @click="$emit('focusWorkingSet',workingSet)">
            <v-list-tile-title>Focus</v-list-tile-title>
          </v-list-tile>
        </v-list>
      </v-menu>
    </v-list-tile-action>
  </v-list-tile>
</template>

<style lang="scss">
</style>
