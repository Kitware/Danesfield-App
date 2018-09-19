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
              name: dataset['name']
            },
            // Quick fix, wait for new GeoJS release
            geometry: JSON.parse(JSON.stringify(dataset['geometa']['bounds']))
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
