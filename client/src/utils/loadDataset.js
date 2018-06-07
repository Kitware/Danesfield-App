
import rest from 'girder/src/rest';

export default () => {
    return rest.get('dataset').then(({ data }) => {
        return data;
    });
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
