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
from girder.constants import AccessType
from girder.api.rest import Resource
from girder.models.item import Item
from girder.models.folder import Folder
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
        self.route('GET', (':id', 'evaluationItems',), self.getEvaluationItems)

    @autoDescribeRoute(
        Description('')
        .errorResponse()
        .errorResponse('Read access was denied on the item.', 403)
    )
    @access.user
    def getAll(self, params):
        cursor = WorkingSet().find({})
        return list(WorkingSet().filterResultsByPermission(
            cursor, self.getCurrentUser(), AccessType.READ, 0, 0))

    @autoDescribeRoute(
        Description('')
        .modelParam('id', model=WorkingSet, destName='workingSet', level=AccessType.READ)
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
        data['datasetIds'] = self.normalizeworkingSetDatasets(data['datasetIds'])

        return WorkingSet().create(
            name=data['name'],
            parentWorkingSet=data.get('parentWorkingSet', None),
            datasetIds=data['datasetIds'],
            user=self.getCurrentUser())

    @autoDescribeRoute(
        Description('')
        .modelParam('id', model=WorkingSet, destName='workingSet', level=AccessType.WRITE)
        .jsonParam('data', '', requireObject=True, paramType='body')
        .errorResponse()
        .errorResponse('Read access was denied on the item.', 403)
    )
    @access.user
    def edit(self, workingSet, data, params):
        data.pop('_id', None)
        data['datasetIds'] = self.normalizeworkingSetDatasets(data['datasetIds'])
        workingSet.update(data)
        return WorkingSet().save(workingSet)

    @autoDescribeRoute(
        Description('')
        .modelParam('id', model=WorkingSet, destName='workingSet', level=AccessType.WRITE)
        .errorResponse()
        .errorResponse('Read access was denied on the item.', 403)
    )
    @access.user
    def delete(self, workingSet, params):
        WorkingSet().remove(workingSet)
        return

    def normalizeworkingSetDatasets(self, datasetIds):
        datasetIdsSet = set(datasetIds)
        for datasetId in datasetIds:
            datasetItem = Item().findOne({'_id': ObjectId(datasetId)})
            # first remove all tar items
            if datasetItem['name'].endswith('.tar'):
                datasetIdsSet.remove(datasetId)
            elif datasetItem['name'].endswith('.NTF'):
                # Try to include coresponding MSI or PAN item
                msiOrPans =\
                    list(Item().find(
                        {'$and':
                         [{'_id': {'$ne': ObjectId(datasetId)}},
                          {'name': {'$regex': '^' + datasetItem['name'].split('-')[0] + '.*.NTF$'}}]
                         }))
                if len(msiOrPans) == 1:
                    datasetIdsSet.add(str(msiOrPans[0]['_id']))

        for datasetId in list(datasetIdsSet):
            datasetItem = Item().findOne({'_id': ObjectId(datasetId)})
            if datasetItem['name'].endswith('.NTF'):
                # Include conresponding TAR items
                tarItem = Item().findOne({
                    'name': datasetItem['name'].replace(".NTF", ".tar"),
                    'folderId': datasetItem['folderId']})
                if tarItem:
                    datasetIdsSet.add(str(tarItem['_id']))

        return list(datasetIdsSet)

    @autoDescribeRoute(
        Description('')
        .modelParam('id', model=WorkingSet, destName='workingSet', level=AccessType.READ)
        .errorResponse()
        .errorResponse('Read access was denied on the item.', 403)
    )
    @access.user
    def getEvaluationItems(self, workingSet, params):
        user = self.getCurrentUser()
        if not workingSet['datasetIds']:
            return []
        datasetItem = Item().findOne({'_id': ObjectId(workingSet['datasetIds'][0])})
        itemFolder = Folder().findOne({'_id': datasetItem['folderId']})
        resultFolders = Folder().find({'parentId': itemFolder['parentId']})
        evaluationDatasets = []
        for folder in resultFolders:
            if folder['name'] in evaluationMapping:
                regexes = evaluationMapping[folder['name']]
                cursor = Item().find(
                    {'$and': [
                        {'folderId': folder['_id']},
                        {'$or': [{'name': {'$regex': regex}} for regex in regexes]}
                    ]}
                )
                evaluationDatasets = evaluationDatasets + list(Item().filterResultsByPermission(
                    cursor, user, AccessType.READ, 0, 0))
        return evaluationDatasets

evaluationMapping = {
    'buildings-to-dsm': ['_CLS.tif$', '_DSM.tif$'],
    'classify-materials': ['_MTL.tif$'],
    'fit-dtm': ['_DTM.tif$'],
    'generate-dsm': ['_DSM.tif$'],
    'segment-by-height': ['_CLS.tif$'],
    'texture-mapping': ['^((?!xxxx[.]obj).)*$']
}
