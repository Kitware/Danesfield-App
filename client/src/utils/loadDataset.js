/*#############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
#############################################################################*/

import girder from '../girder';

export default () => {
    return girder.girder.get('dataset').then(({ data }) => {
        return data;
    });
}

export const loadAllDatasets = async () => {
    let { data: datasets } = await girder.girder.get('dataset');
    return datasets;
}

export const loadDatasetByFilterConditions = async (conditions) => {
    var geometryCollection = conditions
        .map((condition) => condition.geojson.geometry)
        .reduce((collection, geometry) => {
            collection.geometries.push(geometry);
            return collection;
        }, { type: 'GeometryCollection', geometries: [] })

    if (geometryCollection.geometries.length) {
        let { data: datasets } = await girder.girder.get('dataset/search', {
            params: {
                geojson: geometryCollection,
                relation: 'intersects'
            }
        });
        return datasets;
    } else {
        return loadAllDatasets();
    }
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
    var { data: savedDataset } = await girder.girder.put(`item/${dataset._id}/metadata`, dataset.meta);
    return savedDataset;
}

export const loadWorkingSetById = async (id) => {
    var { data: workingset } = await girder.girder.get(`workingSet/${id}`);
    return workingset;
}

export const getTilesetFolderId = async (output_folder_id) => {
    var { data: tilesetFolderId } = await girder.girder.get(`resource/${output_folder_id}/path`, { params: { type: "folder" }});
    return tilesetFolderId;
}
