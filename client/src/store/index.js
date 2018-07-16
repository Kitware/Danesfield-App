import Vue from 'vue';
import Vuex from 'vuex';

import girder from '../girder';
import prompt from "../components/prompt/module";
import filter from './modules/filter';
import workingSet from './modules/workingSet';

Vue.use(Vuex);

export default new Vuex.Store({
  state() {
    return {
      workingSets: [],
      filters: [],
      exploreTab: 'workingSet',
      selectedWorkingSetId: null,
      workspaces: getInitialWorkspace(),
      focusedWorkspaceKey: '0'
    }
  },
  mutations: {
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
      Vue.set(state.workspaces, Math.random().toString(36).substring(7), {
        type: workspace.type,
        datasets: []
      })
    },
    removeWorkspace(state, key) {
      Vue.delete(state.workspaces, key);
    },
    changeWorkspaceType(state, { workspace, type }) {
      workspace.type = type;
      workspace.datasets = [];
    },
    setFocusedWorkspaceKey(state, key) {
      state.focusedWorkspaceKey = key;
    },
    addDatasetToWorkspace(state, { dataset, workspace }) {
      workspace.datasets.push(dataset);
    },
    removeDatasetFromWorkspace(state, { dataset, workspace }) {
      workspace.datasets.splice(workspace.datasets.indexOf(dataset), 1);
    },
    removeAllDatasetsFromWorkspaces(state) {
      for (let workspace of Object.values(state.workspaces)) {
        workspace.datasets = [];
      }
    },
    resetWorkspace(state) {
      state.workspaces = getInitialWorkspace();
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
    }
  },
  getters: {
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

function getInitialWorkspace() {
  return {
    '0': {
      type: 'map',
      datasets: []
    }
  }
}