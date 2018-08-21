import girder from '../girder';

export default () => {
    return girder.girder.get('dataset').then(({ data }) => {
        return data;
    });
}

export const loadDatasetByFilterConditions = async (conditions) => {
    var geometryCollection = conditions
        .map((condition) => condition.geojson.geometry)
        .reduce((collection, geometry) => {
            collection.geometries.push(geometry);
            return collection;
        }, { type: 'GeometryCollection', geometries: [] })

    var result;
    if (geometryCollection.geometries.length) {
        result = await girder.girder.get('item/geometa', {
            params: {
                geojson: geometryCollection,
                relation: 'within'
            }
        });
    } else {
        result = await girder.girder.get('dataset');
    }
    return result.data;
}

export const loadDatasetByIds = (ids) => {
    return Promise.all(ids.map(id => {
        return girder.girder.get(`dataset/${id}`)
            .then(({ data }) => data)
            .catch(() => null)
    })).then(datasets => {
        return datasets.filter(dataset => dataset)
    });
}

export const loadDatasetByWorkingSetId = async (id) => {
    var { data: datasets } = await girder.girder.get(`dataset/workingset/${id}`);
    return datasets;
}

export const saveDatasetMetadata = async (dataset) => {
    var { data: dataset } = await girder.girder.put(`item/${dataset._id}/metadata`, dataset.meta);
    return dataset;
}
