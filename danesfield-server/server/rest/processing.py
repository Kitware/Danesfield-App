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
from girder.api.rest import Resource, RestException, filtermodel, getApiUrl, getCurrentToken
from girder.constants import AccessType
from girder.models.collection import Collection
from girder.models.folder import Folder
from girder.models.item import Item
from girder.models.user import User
from girder.plugins.jobs.models.job import Job

from .. import algorithms
from ..models import workingSet
from ..request_info import RequestInfo


class ProcessingResource(Resource):
    """
    API endpoints to run Danesfield algorithm jobs.
    """
    def __init__(self):
        super(ProcessingResource, self).__init__()

        self.resourceName = 'processing'

        self.route('POST', ('process',), self.process)
        self.route('POST', ('fit_dtm',), self.fitDtm)
        self.route('POST', ('generate_dsm',), self.generateDsm)
        self.route('POST', ('generate_point_cloud',), self.generatePointCloud)

    def _datasetsFolder(self):
        """
        Return the datasets folder document. Creates a collection and folder if necessary.
        """
        # FIXME: Folder is accessible only to admin
        adminUser = User().getAdmins().next()
        collection = Collection().createCollection(
            name='core3d', creator=adminUser, description='', public=True, reuseExisting=True)
        folder = Folder().createFolder(
            parent=collection, name='datasets', parentType='collection', public=False,
            creator=adminUser, reuseExisting=True)
        return folder

    def _fileFromItem(self, item):
        """
        Return the file contained in an item. Raise an exeception if the item doesn't contain
        exactly one file.
        """
        files = Item().childFiles(item, limit=2)
        if files.count() != 1:
            raise RestException(
                'Item must contain %d files, but should contain only one.' % files.count())
        return files[0]

    @access.user
    @autoDescribeRoute(
        Description('Run the complete processing workflow.')
        .notes('Call this endpoint to run the complete processing workflow.\n\n'
               'Options may be provided for individual steps by passing a JSON object '
               'in the **options** parameter. For example:\n\n'
               '```\n'
               '{\n'
               '    "generate-point-cloud": {\n'
               '        "longitude": -84.084032161833051,\n'
               '        "latitude": 39.780404255857590,\n'
               '        "longitudeWidth": 0.008880209782049,\n'
               '        "latitudeWidth": 0.007791684155826\n'
               '    },\n'
               '    "fit-dtm": {\n'
               '        "iterations": 100,\n'
               '        "tension": 10\n'
               '    },\n'
               '    "orthorectify": {\n'
               '        "occlusionThreshold": 1.0,\n'
               '        "denoiseRadius": 2.0\n'
               '    }\n'
               '}\n'
               '```\n')
        .modelParam('workingSet', 'The ID of the working set.', model=workingSet.WorkingSet,
                    paramType='query')
        .jsonParam('options', 'Processing options keyed by step name.', requireObject=True,
                   required=False)
        .errorResponse()
        .errorResponse('Read access was denied on the item.', 403)
    )
    def process(self, workingSet, options, params):
        """
        Run the complete processing workflow.
        """
        user = self.getCurrentUser()
        apiUrl = getApiUrl()
        token = getCurrentToken()
        outputFolder = self._datasetsFolder()

        requestInfo = RequestInfo(user=user, apiUrl=apiUrl, token=token)
        return algorithms.process(
            requestInfo, workingSet=workingSet, outputFolder=outputFolder, options=options)

    @access.user
    @filtermodel(model=Job)
    @autoDescribeRoute(
        Description('Fit a Digital Terrain Model (DTM) to a Digital Surface Model (DSM).')
        .modelParam('itemId', 'The ID of the DSM image item.', model=Item, paramType='query',
                    level=AccessType.READ)
        .param('iterations', 'Base number of iterations at the coarsest scale.',
               dataType='integer', required=False, default=100)
        .param('tension', 'Number of inner smoothing iterations.',
               dataType='integer', required=False, default=10)
        .param('trigger', 'Whether to trigger the next step in the workflow.', dataType='boolean',
               required=False, default=False)
        .errorResponse()
        .errorResponse('Read access was denied on the item.', 403)
    )
    def fitDtm(self, item, iterations, tension, trigger, params):
        """
        Fit a Digital Terrain Model (DTM) to a Digital Surface Model (DSM).
        """
        user = self.getCurrentUser()
        apiUrl = getApiUrl()
        token = getCurrentToken()
        file = self._fileFromItem(item)
        outputFolder = self._datasetsFolder()

        requestInfo = RequestInfo(user=user, apiUrl=apiUrl, token=token)
        return algorithms.fitDtm(
            requestInfo=requestInfo, jobId=None, trigger=trigger, file=file,
            outputFolder=outputFolder, iterations=iterations, tension=tension)

    @access.user
    @filtermodel(model=Job)
    @autoDescribeRoute(
        Description('Generate a Digital Surface Model (DSM) from a point cloud.')
        .modelParam('itemId', 'The ID of the point cloud item.', model=Item, paramType='query',
                    level=AccessType.READ)
        .param('trigger', 'Whether to trigger the next step in the workflow.', dataType='boolean',
               required=False, default=False)
        .errorResponse()
        .errorResponse('Read access was denied on the item.', 403)
    )
    def generateDsm(self, item, trigger, params):
        """
        Generate a Digital Surface Model (DSM) from a point cloud.
        """
        # TODO: generate-dsm.py supports multiple point cloud files as input. To support
        # that workflow, this endpoint could accept a JSON list of file IDs.
        user = self.getCurrentUser()
        apiUrl = getApiUrl()
        token = getCurrentToken()
        file = self._fileFromItem(item)
        outputFolder = self._datasetsFolder()

        requestInfo = RequestInfo(user=user, apiUrl=apiUrl, token=token)
        return algorithms.generateDsm(
            requestInfo=requestInfo, jobId=None, trigger=trigger, file=file,
            outputFolder=outputFolder)

    @access.user
    @filtermodel(model=Job)
    @autoDescribeRoute(
        Description('Generate a point cloud from images.')
        .jsonParam('imageItemIds', 'The IDs of the input image items as a JSON array.',
                   requireArray=True)
        .param('longitude', 'The longitude of the center of the point cloud, in decimal degrees.',
               dataType='double')
        .param('latitude', 'The latitude of the center of the point cloud, in decimal degrees.',
               dataType='double')
        .param('longitudeWidth',
               'The longitudinal dimension of the point cloud, in decimal degrees.',
               dataType='double')
        .param('latitudeWidth',
               'The latitudinal dimension of the point cloud, in decimal degrees.',
               dataType='double')
        .param('trigger', 'Whether to trigger the next step in the workflow.', dataType='boolean',
               required=False, default=False)
        .errorResponse()
        .errorResponse('Read access was denied on the items.', 403)
    )
    def generatePointCloud(self, imageItemIds, longitude, latitude, longitudeWidth, latitudeWidth,
                           trigger, params):
        """
        Generate a 3D point cloud from 2D images.

        Requirements:
        - p3d_gw Docker image is available on host
        - Host folder /mnt/GTOPO30 contains GTOPO 30 data
        """
        user = self.getCurrentUser()
        apiUrl = getApiUrl()
        token = getCurrentToken()
        outputFolder = self._datasetsFolder()

        # Get file IDs from image item IDs
        imageFileIds = [
            self._fileFromItem(Item().load(itemId, level=AccessType.READ, user=user))['_id']
            for itemId in imageItemIds
        ]

        requestInfo = RequestInfo(user=user, apiUrl=apiUrl, token=token)
        return algorithms.generatePointCloud(
            requestInfo=requestInfo, jobId=None, trigger=trigger, imageFileIds=imageFileIds,
            outputFolder=outputFolder, longitude=longitude, latitude=latitude,
            longitudeWidth=longitudeWidth, latitudeWidth=latitudeWidth)
