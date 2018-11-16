/*#############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
#############################################################################*/

import girder from '../../girder';
import { loadDatasetByWorkingSetId, loadDatasetByFilterConditions } from "../../utils/loadDataset";

export default {
  namespaced: true,
  state: {
    editingWorkingSet: null,
    datasets: [],
    selectedDataset: null,
    selectedCondition: null,
    uploadGeojsonDialog: false,
    editingConditions: [],
  },
  mutations: {
    setEditingWorkingSet(state, workingSet) {
      state.editingWorkingSet = workingSet;
    },
    setDatasets(state, datasets) {
      state.datasets = datasets;
    },
    setSelectedDataset(state, dataset) {
      state.selectedDataset = dataset;
    },
    setSelectedCondition(state, condition) {
      state.selectedCondition = condition;
    },
    setUploadGeojsonDialog(state, value) {
      state.uploadGeojsonDialog = value;
    },
    clear(state) {
      state.datasets = [];
      state.editingConditions = [];
      state.editingWorkingSet = null;
    }
  },
  actions: {
    async loadDatasetByFilterConditions({ commit, state }, conditions) {
      commit('setDatasets', []);
      var datasets = await loadDatasetByFilterConditions(conditions);
      commit('setDatasets', datasets);
    },
    async loadDatasetByWorkingSetId({ commit, state }, workingSetId) {
      commit('setDatasets', []);
      let datasets = await loadDatasetByWorkingSetId(workingSetId);
      commit('setDatasets', datasets);
    },
    async loadConditionsByFilter({ commit, state }, filterId) {
      let { data: filter } = await girder.girder.get(`filter/${filterId}`);
      state.editingConditions = filter.conditions;
    }
  },
  getters: {
    editingConditionsGeojson(state) {
      if (!state.editingConditions) {
        return null;
      }
      return {
        type: "FeatureCollection",
        features: state.editingConditions
          .filter(
            condition =>
              condition.type === "region"
          )
          .map(condition => condition.geojson)
      };
    },
    editingSelectedConditionGeojson(state) {
      if (
        !state.selectedCondition ||
        state.selectedCondition.type !== "region"
      ) {
        return null;
      }
      return state.selectedCondition.geojson;
    }
  }
};
