export default {
  namespaced: true,
  state: {
    editingWorkingSet: null,
    datasets: []
  },
  mutations: {
    setEditingWorkingSet(state, workingSet) {
      state.editingWorkingSet = workingSet;
    },
    setDatasets(state, datasets) {
      state.datasets = datasets;
    }
  },
  actions: {},
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
    datasetBoundsFeature(state) {
      return state.datasets.reduce((featureCollection, dataset) => {
        featureCollection.features.push({
          type: 'Feature',
          properties: {
            name: dataset['name']
          },
          geometry: dataset['geometa']['bounds']
        });
        return featureCollection;
      }, { type: "FeatureCollection", features: [] });
    }
  }
};
