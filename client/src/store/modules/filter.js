import rest from 'girder/src/rest';
import _ from 'lodash';
import { polygon } from '@turf/helpers';
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
    datasetBounds: []
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
    setDatasetBounds(state, datasetBounds) {
      state.datasetBounds = datasetBounds;
    }
  },
  actions: {
    async loadBounds({ commit, state }, conditions) {
      var datasets = await loadDatasetByFilterConditions(conditions);
      return state.datasetBounds = datasets.map(dataset => {
        return {
          name: dataset['name'],
          bounds: dataset['geometa']['bounds']
        }
      });
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
              condition.type === "region" &&
              condition !== state.selectedCondition
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
      return state.datasetBounds.map(datasetBound => {
        // console.log(datasetBound.bounds);
        // let geojson = polygon([datasetBound.bounds]);
        let point = pointOnFeature(datasetBound.bounds);
        return {
          x: point.geometry.coordinates[0],
          y: point.geometry.coordinates[1],
          name: datasetBound.name
        }
      });
    }
  }
};
