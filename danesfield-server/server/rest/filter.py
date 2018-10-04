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
from ..models.filter import Filter


class FilterResource(Resource):

    def __init__(self):
        super(FilterResource, self).__init__()

        self.resourceName = 'filter'
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
        cursor = Filter().find({})
        return list(Filter().filterResultsByPermission(
            cursor, self.getCurrentUser(), AccessType.READ, 0, 0))

    @autoDescribeRoute(
        Description('')
        .modelParam('id', model=Filter, destName='filter', level=AccessType.READ)
        .errorResponse()
        .errorResponse('Read access was denied on the item.', 403)
    )
    @access.user
    def get(self, filter, params):
        return filter

    @autoDescribeRoute(
        Description('')
        .jsonParam('data', '', requireObject=True, paramType='body')
        .errorResponse()
        .errorResponse('Read access was denied on the item.', 403)
    )
    @access.user
    def create(self, data, params):
        return Filter().create(data, user=self.getCurrentUser())

    @autoDescribeRoute(
        Description('')
        .modelParam('id', model=Filter, destName='filter', level=AccessType.WRITE)
        .jsonParam('data', '', requireObject=True, paramType='body')
        .errorResponse()
        .errorResponse('Read access was denied on the item.', 403)
    )
    @access.user
    def edit(self, filter, data, params):
        data.pop('_id', None)
        filter.update(data)
        return Filter().save(filter)

    @autoDescribeRoute(
        Description('')
        .modelParam('id', model=Filter, destName='filter', level=AccessType.WRITE)
        .errorResponse()
        .errorResponse('Read access was denied on the item.', 403)
    )
    @access.user
    def delete(self, filter, params):
        Filter().remove(filter)
        return
