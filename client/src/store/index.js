import Vue from 'vue';
import Vuex from 'vuex';

import girder from '../girder';
import prompt from "resonantgeoview/src/components/prompt/module";
import filter from './modules/filter';
import workingSet from './modules/workingSet';
import paletteColors from '../components/vtk/paletteColors';
import { loadAllDatasets } from '../utils/loadDataset';

Vue.use(Vuex);

export default new Vuex.Store({
  state() {
    return {
      sidePanelExpanded: true,
      workingSets: [],
      filters: [],
      // For always showing datasets on Explore
      allDatasets: [],
      exploreTab: 'workingSet',
      hideUnsupportedDatasetsOnFocus: false,
      selectedWorkingSetId: null,
      workspaces: getInitialWorkspace(),
      focusedWorkspaceKey: '0',
      vtkBGColor: paletteColors[paletteColors.length - 1]
    }
  },
  mutations: {
    toggleSidePanel(state) {
      state.sidePanelExpanded = !state.sidePanelExpanded;
    },
    setExploreTab(state, value) {
      state.exploreTab = value;
      this.commit("filter/setEditingFilter", null);
      this.commit('workingSet/setEditingWorkingSet', null);
    },
    addWorkingSet(state, workingSet) {
      state.workingSets.push(workingSet);
    },
    setSelectWorkingSetId(state, workingSetId) {
      state.selectedWorkingSetId = workingSetId;
    },
    addFilter(state, filter) {
      state.filters.push(filter);
    },
    createWorkingSetFromFilter(state, filter) {
      var workingSet = { name: '', filterId: filter._id, datasetIds: [] };
      state.exploreTab = 'workingSet';
      state.workingSet.editingWorkingSet = workingSet;
    },
    addWorkspace(state, workspace) {
      var newWorkspace = {
        type: workspace.type,
        layers: []
      };
      switch (newWorkspace.type) {
        case 'vtk':
          newWorkspace.texture = true;
          break;
        case 'map':
          break;
      }
      Vue.set(state.workspaces, Math.random().toString(36).substring(7), newWorkspace);
    },
    removeWorkspace(state, key) {
      Vue.delete(state.workspaces, key);
    },
    changeWorkspaceType(state, { workspace, type }) {
      workspace.type = type;
      workspace.layers = [];
      switch (workspace.type) {
        case 'vtk':
          Vue.set(workspace, 'texture', true);
          break;
        case 'map':
          Vue.delete(workspace, 'texture');
          break;
      }
    },
    setFocusedWorkspaceKey(state, key) {
      state.focusedWorkspaceKey = key;
    },
    addDatasetToWorkspace(state, { dataset, workspace }) {
      workspace.layers.push({ dataset, opacity: 1 });
    },
    removeDatasetFromWorkspace(state, { dataset, workspace }) {
      workspace.layers.splice(workspace.layers.map(layers => layers.dataset).indexOf(dataset), 1);
    },
    removeAllDatasetsFromWorkspaces(state) {
      for (let workspace of Object.values(state.workspaces)) {
        workspace.layers = [];
      }
    },
    resetWorkspace(state) {
      state.workspaces = getInitialWorkspace();
    },
    changeVTKBGColor(state, color) {
      state.vtkBGColor = color;
    },
    setWorkspaceLayers(state, { workspace, layers }) {
      workspace.layers = layers;
    },
    setWorkspaceLayerOpacity(state, { layer, opacity }) {
      layer.opacity = opacity;
    },
    toggleHideUnsupportedDatasets(state) {
      state.hideUnsupportedDatasetsOnFocus = !state.hideUnsupportedDatasetsOnFocus;
    }
  },
  actions: {
    loadWorkingSets() {
      girder.girder.get('workingSet')
        .then(({ data }) => {
          this.state.workingSets = data;
        });
    },
    saveWorkingSet({ commit, state }, workingSet) {
      if (workingSet._id) {
        return girder.girder.put(`workingSet/${workingSet._id}`, workingSet)
          .then(({ data }) => {
            let existing = state.workingSets.filter(workingSet1 => workingSet1._id === workingSet._id)[0];
            Object.assign(existing, data);
            return data;
          });
      } else {
        return girder.girder.post('workingSet', workingSet)
          .then(({ data }) => {
            commit('addWorkingSet', data);
            return data;
          })
      }
    },
    deleteWorkingSet({ commit, state }, workingSet) {
      if (this.state.selectedWorkingSetId === workingSet._id) {
        this.commit("setSelectWorkingSetId", null);
      }
      return girder.girder.delete(`workingSet/${workingSet._id}`).then(() => {
        this.state.workingSets.splice(this.state.workingSets.indexOf(workingSet), 1);
        return workingSet;
      });
    },
    loadFilters() {
      girder.girder.get('filter')
        .then(({ data }) => {
          this.state.filters = data;
        });
    },
    saveFilter({ commit, state }, filter) {
      if (filter._id) {
        return girder.girder.put(`filter/${filter._id}`, filter)
          .then(({ data }) => {
            let existing = state.filters.filter(filter1 => filter1._id === filter._id)[0];
            Object.assign(existing, data);
            return data;
          });
      } else {
        return girder.girder.post('filter', filter)
          .then(({ data }) => {
            commit('addFilter', data);
            return data;
          })
      }
    },
    deleteFilter({ commit, state }, filter) {
      return girder.girder.delete(`filter/${filter._id}`).then(() => {
        this.state.filters.splice(this.state.filters.indexOf(filter), 1);
        return filter;
      });
    },
    async loadAllDatasets({ state }) {
      state.allDatasets = await loadAllDatasets();
    }
  },
  getters: {
    flattenedWorkingSets(state) {
      return flattenWorkingSets(treefyWorkingSets(state.workingSets));
    },
    focusedWorkspace(state) {
      return state.workspaces[state.focusedWorkspaceKey] || Object.values(state.workspaces)[0];
    }
  },
  modules: {
    filter,
    workingSet,
    prompt
  }
});

function treefyWorkingSets(workingSets) {
  var mapping = new Map();
  var tree = [];
  for (let workingSet of workingSets) {
    let id = workingSet._id;
    let node = { id, workingSet, children: [] };
    mapping.set(id, node);
    if (!workingSet.parentWorkingSetId) {
      tree.push(node);
    } else {
      if (mapping.has(workingSet.parentWorkingSetId)) {
        mapping.get(workingSet.parentWorkingSetId).children.push(node);
      } else {
        tree.push(node);
      }
    }
  }
  return tree;
}

function flattenWorkingSets(children, level = 0) {
  var output = [];
  for (let node of children) {
    output.unshift({ workingSet: node.workingSet, level });
    if (node.children.length) {
      output.splice(1, 0, ...flattenWorkingSets(node.children, level + 1));
    }
  }
  return output;
}

function getInitialWorkspace() {
  return {
    '0': {
      type: 'map',
      layers: []
    }
  }
}
