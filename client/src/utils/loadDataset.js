import girder from '../girder';

export default () => {
    return girder.rest.get('dataset').then(({ data }) => {
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
        result = await girder.rest.get('item/geometa', {
            params: {
                geojson: geometryCollection,
                relation: 'within'
            }
        });
    } else {
        result = await girder.rest.get('dataset');
    }
    return result.data;
}

export const loadDatasetById = (ids) => {
    return Promise.all(ids.map(id => {
        return girder.rest.get(`dataset/${id}`)
            .then(({ data }) => data)
            .catch(() => null)
    })).then(datasets => {
        return datasets.filter(dataset => dataset)
    });
}
