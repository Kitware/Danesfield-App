
import rest from 'girder/src/rest';

export default (dataset) => {
    return rest.get(`item/${dataset._id}/download`)
        .then(({ data }) => {
            return data;
        });
}
