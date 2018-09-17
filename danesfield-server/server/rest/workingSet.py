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

from bson.objectid import ObjectId
from girder.api import access
from girder.api.describe import autoDescribeRoute, Description
from girder.api.rest import Resource
from girder.models.item import Item
from ..models.workingSet import WorkingSet


class WorkingSetResource(Resource):

    def __init__(self):
        super(WorkingSetResource, self).__init__()

        self.resourceName = 'workingSet'
        self.route('GET', (), self.getAll)
        self.route('GET', (':id',), self.get)
        self.route('POST', (), self.create)
        self.route('PUT', (':id',), self.edit)
        self.route('DELETE', (':id',), self.delete)

    @autoDescribeRoute(
        Description('')
        .errorResponse()
        .errorResponse('Read access was denied on the item.', 403)
    )
    @access.user
    def getAll(self, params):
        return list(WorkingSet().find({}))

    @autoDescribeRoute(
        Description('')
        .modelParam('id', model=WorkingSet, destName='workingSet')
        .errorResponse()
        .errorResponse('Read access was denied on the item.', 403)
    )
    @access.user
    def get(self, workingSet, params):
        return workingSet

    @autoDescribeRoute(
        Description('')
        .jsonParam('data', '', requireObject=True, paramType='body')
        .errorResponse()
        .errorResponse('Read access was denied on the item.', 403)
    )
    @access.user
    def create(self, data, params):
        datasetIds = set(data['datasetIds'])
        for datasetId in data['datasetIds']:
            datasetItem = Item().findOne({'_id': ObjectId(datasetId)})
            if not datasetItem['name'].endswith('.NTF'):
                continue
            # Include conresponding TAR files
            tarItem = Item().findOne({
                'name': datasetItem['name'].replace(".NTF", ".tar"),
                'folderId': datasetItem['folderId']})
            if tarItem:
                datasetIds.add(str(tarItem['_id']))
            # Try to include coresponding MSI or PAN file
            msiOrPans =\
                list(Item().find(
                    {'$and':
                     [{'_id': {'$ne': ObjectId(datasetId)}},
                      {'name': {'$regex': '^' + datasetItem['name'].split('_')[0] + '.^.NTF$'}}]
                     }))
            if len(msiOrPans) == 1:
                datasetIds.add(str(msiOrPans[0]['_id']))

        data['datasetIds'] = list(datasetIds)
        return WorkingSet().save(data)

    @autoDescribeRoute(
        Description('')
        .modelParam('id', model=WorkingSet, destName='workingSet')
        .jsonParam('data', '', requireObject=True, paramType='body')
        .errorResponse()
        .errorResponse('Read access was denied on the item.', 403)
    )
    @access.user
    def edit(self, workingSet, data, params):
        data.pop('_id', None)
        workingSet.update(data)
        return WorkingSet().save(workingSet)

    @autoDescribeRoute(
        Description('')
        .modelParam('id', model=WorkingSet, destName='workingSet')
        .errorResponse()
        .errorResponse('Read access was denied on the item.', 403)
    )
    @access.user
    def delete(self, workingSet, params):
        WorkingSet().remove(workingSet)
        return
