
import rest from 'girder/src/rest';

export default () => {
    return rest.get('dataset').then(({ data }) => {
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
        result = await rest.get('item/geometa', {
            params: {
                geojson: geometryCollection,
                relation: 'within'
            }
        });
    } else {
        result = await rest.get('dataset');
    }
    return result.data;
}

export const loadDatasetById = (ids) => {
    return Promise.all(ids.map(id => {
        return rest.get(`dataset/${id}`)
            .then(({ data }) => data)
            .catch(() => null)
    })).then(datasets => {
        return datasets.filter(dataset => dataset)
    });
}
