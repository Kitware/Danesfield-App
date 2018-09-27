import pointOnFeature from '@turf/point-on-feature';

export default {
  namespaced: true,
  state: {
    editingWorkingSet: null,
    datasets: [],
    selectedDataset: null
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
    }
  },
  actions: {},
  getters: {
    datasetBoundsFeature(state) {
      return state.datasets
        .filter(dataset =>
          dataset['geometa'] && dataset['geometa']['bounds']
        ).reduce((featureCollection, dataset) => {
          featureCollection.features.push({
            type: 'Feature',
            properties: {
              name: dataset['name'],
              _id: dataset._id
            },
            geometry: dataset['geometa']['bounds']
          });
          return featureCollection;
        }, { type: "FeatureCollection", features: [] });
    },
    selectedDatasetPoint(state) {
      if (!state.selectedDataset || !state.selectedDataset.geometa) {
        return null;
      }
      return pointOnFeature(state.selectedDataset.geometa.bounds).geometry;
    }
  }
};
