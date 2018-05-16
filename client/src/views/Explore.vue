

<template>
  <FullScreenViewport>
    <GeojsMapViewport
      class='map'
      :viewport.sync='viewport'
    >
      <GeojsTileLayer
        url='https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png'
        attribution='© OpenStreetMap contributors, © CARTO'>
      </GeojsTileLayer>
      <GeojsAnnotationLayer
        :drawing.sync='drawing'
        :editing.sync='editing'
        :editable='true'
        :annotations.sync='annotations'>
      </GeojsAnnotationLayer>
      <GeojsGeojsonLayer
        :geojson='workingSetRegions'>
      </GeojsGeojsonLayer>
    </GeojsMapViewport>

    <SidePanel
    :top='64'
    :toolbar='{title: "Working Sets"}'
    :expanded='true'
    :footer='false'
    >
      <template slot='actions'>
        <SidePanelAction
        v-for="action in actions" 
        :key='action.name'
        @click.stop='drawing = action.name'>
        <v-icon>{{action.icon}}</v-icon>
        </SidePanelAction>
      </template>
      <v-expansion-panel v-if='!editingWorkingSet'>
        <v-expansion-panel-content
          v-for="workingSet in workingSets" 
          :key="workingSet.name">
          <div slot='header'>{{workingSet.name}}</div>
          <v-container grid-list-xs>
            <v-layout row wrap>
              <v-flex xs2 offset-xs1>
                <v-btn block color='grey lighten-3' depressed @click="editingWorkingSet=workingSet">
                  <v-icon>edit</v-icon>
                </v-btn>
              </v-flex>
              <v-flex xs4 offset-xs4>
                <v-btn block color='primary' class='' depressed @click="focusWorkingSet(workingSet)">
                  Focus
                  <v-icon class='pl-1'>center_focus_strong</v-icon>
                </v-btn>
              </v-flex>
            </v-layout>
          </v-container>
        </v-expansion-panel-content>
      </v-expansion-panel>
      <new-working-set v-if='!editingWorkingSet' default='working-set-1' @confirm='addNewWorkingSet' />
      <EditWorkingSet 
      v-if='editingWorkingSet'
      :annotations.sync='annotations'
      :workingSet.sync='editingWorkingSet' />
    </SidePanel>
  </FullScreenViewport>
</template>

<style lang="scss" scoped>
.map {
  z-index: 0;
}
// overwrite
.expansion-panel {
  box-shadow: none;
}
</style>
<script>
import { mapState } from "vuex";

import NewWorkingSet from "../components/NewWorkingSet";
import EditWorkingSet from "../components/EditWorkingSet";

export default {
  name: "explore",
  components: {
    NewWorkingSet,
    EditWorkingSet
  },
  data() {
    return {
      editingWorkingSet: null,
      annotations: [],
      viewport: {
        center: [-100, 30],
        zoom: 4
      },
      drawing: false,
      editing: false
    };
  },
  computed: {
    actions() {
      if (this.editingWorkingSet) {
        return [{ name: "rectangle", icon: "aspect_ratio" }];
      }
      return [];
    },
    workingSetRegions() {
      if (!this.editingWorkingSet) {
        return {
          type: "Point",
          coordinates: [98.0859375, 47.27922900257082]
        };
      }
      return {
        type: "FeatureCollection",
        features: this.editingWorkingSet.filters
          .filter(filter => filter.type === "region")
          .map(filter => filter.geojson)
      };
    },
    ...mapState(["workingSets"])
  },
  created() {
    this.$store.dispatch("loadWorkingSets");
  },
  methods: {
    clickAction(drawing) {
      this.drawing = drawing;
    },
    clearItems() {
      this.panel.items = 0;
    },
    addNewWorkingSet(name) {
      this.$store.dispatch("tryAddWorkingSets", name).then(workingSet => {
        if (workingSet) {
          this.editingWorkingSet = workingSet;
        }
      });
    },
    focusWorkingSet(workingSet) {
      this.$store.commit("selectWorkingSetId", workingSet._id);
      this.$router.push("focus");
    }
  }
};
</script>
