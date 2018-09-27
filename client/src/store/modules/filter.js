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
    },
    heatmapData(state) {
      return state.datasets.map(dataset => {
        let point = pointOnFeature(dataset.geometa.bounds);
        return point.geometry.coordinates;
      });
    },
    datasetBoundsFeature(state) {
      return state.datasets
        .filter(dataset =>
          dataset['geometa'] && dataset['geometa']['bounds']
        ).reduce((featureCollection, dataset) => {
          featureCollection.features.push({
            type: 'Feature',
            properties: {
              name: dataset.name,
              _id: dataset._id
            },
            geometry: dataset['geometa']['bounds']
          });
          return featureCollection;
        }, { type: "FeatureCollection", features: [] });
    },
    selectedDatasetPoint(state) {
      if (!state.selectedDataset) {
        return null;
      }
      return pointOnFeature(state.selectedDataset.geometa.bounds).geometry;
    }
  }
};
