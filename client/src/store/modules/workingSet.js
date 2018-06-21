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
      var point = pointOnFeature(state.selectedDataset.geometa.bounds);
      return {
        _id: state.selectedDataset._id,
        name: state.selectedDataset.name,
        x: point.geometry.coordinates[0],
        y: point.geometry.coordinates[1]
      }
    }
  }
};
