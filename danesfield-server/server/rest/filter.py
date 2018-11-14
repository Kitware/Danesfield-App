#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
###############################################################################



from girder.api import access
from girder.api.describe import autoDescribeRoute, Description
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
        return list(Filter().find({}))

    @autoDescribeRoute(
        Description('')
        .modelParam('id', model=Filter, destName='filter')
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
        return Filter().save(data)

    @autoDescribeRoute(
        Description('')
        .modelParam('id', model=Filter, destName='filter')
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
        .modelParam('id', model=Filter, destName='filter')
        .errorResponse()
        .errorResponse('Read access was denied on the item.', 403)
    )
    @access.user
    def delete(self, filter, params):
        Filter().remove(filter)
        return
