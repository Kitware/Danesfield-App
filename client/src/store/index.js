import Vue from 'vue'
import Vuex from 'vuex'

import auth from 'girder/src/store/auth';
import rest from 'girder/src/rest';

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    workingSets: [],
    selectedWorkingSetId: null
  },
  mutations: {
    addWorkingSets(state, workingSet) {
      this.state.workingSets.push(workingSet);
    },
    selectWorkingSetId(state, workingSetId) {
      this.state.selectedWorkingSetId = workingSetId;
    }
  },
  actions: {
    loadWorkingSets() {
      rest.get('workingSet')
        .then(({ data }) => {
          this.state.workingSets = data;
        });
    },
    tryAddWorkingSets({ commit, state }, name) {
      var workingSet = { name, filters: [] };
      return rest.post('workingSet', workingSet)
        .then((({ data }) => {
          commit('addWorkingSets', data);
          return data;
        }));
    },
    saveWorkingSet({ commit, state }, workingSet) {
      return rest.put(`workingSet/${workingSet._id}`, workingSet);
    },
    deleteWorkingSet({ commit, state }, workingSet) {
      if (this.state.selectedWorkingSetId === workingSet._id) {
        this.commit("selectWorkingSetId", null);
      }
      return rest.delete(`workingSet/${workingSet._id}`).then(() => {
        this.state.workingSets.splice(this.state.workingSets.indexOf(workingSet), 1);
        return workingSet;
      });
    }
  },
  modules: {
    auth
  }
});
