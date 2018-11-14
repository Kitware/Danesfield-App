/*#############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
#############################################################################*/

import girder from '../girder';

export default (dataset) => {
    return girder.girder.get(`item/${dataset._id}/download`)
        .then(({ data }) => {
            return data;
        });
}
