/*#############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
#############################################################################*/

import pointOnFeature from '@turf/point-on-feature';

import { loadDatasetByFilterConditions } from "../../utils/loadDataset";

export default {
  namespaced: true,
  state: {
    editingFilter: null,
    selectedCondition: null,
    annotations: [],
    pickDateRange: false,
    uploadGeojsonDialog: false,
    editingConditions: null,
    datasets: [],
    selectedDataset: null
  },
  mutations: {
    setEditingFilter(state, filter) {
      state.editingFilter = filter;
      if (!filter) {
        state.selectedCondition = null;
        state.editingConditions = null;
      }
    },
    setSelectedCondition(state, condition) {
      state.selectedCondition = condition;
    },
    setAnnotations(state, annotations) {
      state.annotations = annotations;
    },
    setPickDateRange(state, value) {
      state.pickDateRange = value;
    },
    setUploadGeojsonDialog(state, value) {
      state.uploadGeojsonDialog = value;
    },
    setEditingConditions(state, conditions) {
      state.editingConditions = conditions;
    },
    setDatasets(state, datasets) {
      state.datasets = datasets;
    },
    setSelectedDataset(state, dataset) {
      state.selectedDataset = dataset;
    }
  },
  actions: {
    async loadDatasets({ commit, state }, conditions) {
      var datasets = await loadDatasetByFilterConditions(conditions);
      commit('setDatasets', datasets);
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
