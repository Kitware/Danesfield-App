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
  }
};
