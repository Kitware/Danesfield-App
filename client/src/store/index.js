import Vue from 'vue';
import Vuex from 'vuex';

import auth from 'girder/src/store/auth';
import rest from 'girder/src/rest';

import prompt from "../components/prompt/module";
import filter from './modules/filter';
import workingSet from './modules/workingSet';

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    workingSets: [],
    filters: [],
    exploreTab: 'workingSet',
    selectedWorkingSetId: null
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
    }
  },
  actions: {
    loadWorkingSets() {
      rest.get('workingSet')
        .then(({ data }) => {
          this.state.workingSets = data;
        });
    },
    saveWorkingSet({ commit, state }, workingSet) {
      if (workingSet._id) {
        return rest.put(`workingSet/${workingSet._id}`, workingSet)
          .then(({ data }) => {
            let existing = state.workingSets.filter(workingSet1 => workingSet1._id === workingSet._id)[0];
            Object.assign(existing, data);
            return data;
          });
      } else {
        return rest.post('workingSet', workingSet)
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
      return rest.delete(`workingSet/${workingSet._id}`).then(() => {
        this.state.workingSets.splice(this.state.workingSets.indexOf(workingSet), 1);
        return workingSet;
      });
    },
    loadFilters() {
      rest.get('filter')
        .then(({ data }) => {
          this.state.filters = data;
        });
    },
    saveFilter({ commit, state }, filter) {
      if (filter._id) {
        return rest.put(`filter/${filter._id}`, filter)
          .then(({ data }) => {
            let existing = state.filters.filter(filter1 => filter1._id === filter._id)[0];
            Object.assign(existing, data);
            return data;
          });
      } else {
        return rest.post('filter', filter)
          .then(({ data }) => {
            commit('addFilter', data);
            return data;
          })
      }
    },
    deleteFilter({ commit, state }, filter) {
      return rest.delete(`filter/${filter._id}`).then(() => {
        this.state.filters.splice(this.state.filters.indexOf(filter), 1);
        return filter;
      });
    }
  },
  modules: {
    auth,
    filter,
    workingSet,
    prompt
  }
});
