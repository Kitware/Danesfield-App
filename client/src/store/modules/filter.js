import pointOnFeature from '@turf/point-on-feature';

import { loadDatasetByFilterConditions } from "../../utils/loadDataset";

export default {
  namespaced: true,
  state: {
    editingFilter: null,
    selectedCondition: null,
    annotations: [],
    pickDateRange: false,
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
      state.selectedCondition;
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
    },
    heatmapData(state) {
      return state.datasets.map(dataset => {
        let point = pointOnFeature(dataset.geometa.bounds);
        return {
          _id: dataset._id,
          name: dataset.name,
          x: point.geometry.coordinates[0],
          y: point.geometry.coordinates[1]
        }
      });
    },
    selectedDatasetPoint(state, getters) {
      if (!getters.heatmapData.length || !state.selectedDataset) {
        return null;
      }
      return getters.heatmapData.filter(point => point._id === state.selectedDataset._id)[0];
    }
  }
};
