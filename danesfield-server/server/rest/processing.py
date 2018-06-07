#!/usr/bin/env python
# -*- coding: utf-8 -*-

##############################################################################
#  Copyright Kitware Inc.
#
#  Licensed under the Apache License, Version 2.0 ( the "License" );
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
##############################################################################

from girder.api import access
from girder.api.describe import autoDescribeRoute, Description
from girder.constants import AccessType
from girder.api.rest import Resource
from girder.models.user import User
from girder.models.collection import Collection
from girder.models.folder import Folder
from girder.models.item import Item


class ProcessingResource(Resource):

    def __init__(self):
        super(ProcessingResource, self).__init__()

        self.resourceName = 'processing'
        self.route('POST', (':itemId',), self.dsm)

    @autoDescribeRoute(
        Description('')
        .errorResponse()
        .modelParam('itemId', 'The ID of the point cloud file.', model=Item, level=AccessType.READ)
        .errorResponse('Read access was denied on the item.', 403)
    )
    @access.user
    def dsm(self, item, params):
        pass
        # from girder.plugins.danesfield.api.danesfield import DanesfieldResource
        # file = Item().childFiles(item)[0]

        # adminUser = User().getAdmins().next()
        # collection = Collection().createCollection('core3d', creator=adminUser,
        #                                            description='', public=True, reuseExisting=True)
        # folder = Folder().createFolder(
        #     collection, 'datasets', parentType='collection', public=False,
        #     creator=adminUser, reuseExisting=True)
        # return DanesfieldResource().generateDsm(fileId=file['_id'], outputFolderId=folder['_id'], params={})
