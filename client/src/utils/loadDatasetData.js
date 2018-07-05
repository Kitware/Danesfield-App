import girder from '../girder';

export default (dataset) => {
    return girder.girder.get(`item/${dataset._id}/download`)
        .then(({ data }) => {
            return data;
        });
}
