
import rest from 'girder/src/rest';

export default () => {
    return rest.get('collection', {
        params: {
            text: 'core3d'
        }
    }).then(({ data }) => {
        var collection = data[0];
        return collection;
    }).then((collection) => {
        return rest.get('folder', {
            params: {
                parentType: 'collection',
                parentId: collection._id,
                name: 'datasets'
            }
        }).then(({ data }) => {
            var folder = data[0];
            return folder;
        })
    }).then((folder) => {
        return rest.get('item', {
            params: {
                folderId: folder._id
            }
        }).then(({ data }) => {
            return data;
        })
    });
}

export const loadDatasetById = (ids) => {
    return Promise.all(ids.map(id => {
        return rest.get(`item/${id}`)
            .then(({ data }) => data)
    }));
}
