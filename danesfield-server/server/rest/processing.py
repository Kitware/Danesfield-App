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

import itertools
import json
import os

from girder.api import access
from girder.api.describe import autoDescribeRoute, Description
from girder.api.rest import Resource, RestException, filtermodel
from girder.constants import AccessType
from girder.models.collection import Collection
from girder.models.folder import Folder
from girder.models.item import Item
from girder.models.user import User
from girder.plugins.jobs.models.job import Job

from girder_worker.docker.tasks import docker_run
from girder_worker.docker.transforms import BindMountVolume, VolumePath
from girder_worker.docker.transforms.girder import (
    GirderFileIdToVolume, GirderUploadVolumePathToFolder)


_DANESFIELD_DOCKER_IMAGE = 'core3d/danesfield'
_DANESFIELD_SOURCE_KEY = 'danesfieldSource'

_P3D_DOCKER_IMAGE = 'p3d_gw'


class ProcessingResource(Resource):
    """
    API endpoints to run Danesfield algorithm jobs.
    """
    def __init__(self):
        super(ProcessingResource, self).__init__()

        self.resourceName = 'processing'

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
    @filtermodel(model=Job)
    @autoDescribeRoute(
        Description('Fit a Digital Terrain Model (DTM) to a Digital Surface Model (DSM).')
        .modelParam('itemId', 'The ID of the DSM image item.', model=Item, paramType='query',
                    level=AccessType.READ)
        .param('iterations', 'Base number of iterations at the coarsest scale.',
               dataType='integer', required=False, default=100)
        .param('tension', 'Number of inner smoothing iterations.',
               dataType='integer', required=False, default=10)
        .errorResponse()
        .errorResponse('Read access was denied on the item.', 403)
    )
    def fitDtm(self, item, iterations, tension, params):
        """
        Fit a Digital Terrain Model (DTM) to a Digital Surface Model (DSM).

        Requirements:
        - core3d/danesfield Docker image is available on host
        """
        source = 'fit-dtm'
        file = self._fileFromItem(item)
        outputFolder = self._datasetsFolder()

        # Set output file name based on input file name
        parts = os.path.splitext(file['name'])
        dsmName = '-dtm'.join(parts)
        outputVolumePath = VolumePath(dsmName)

        # Docker container arguments
        containerArgs = [
            'python', 'danesfield/tools/fit-dtm.py',
            '--num-iterations', str(iterations),
            '--tension', str(tension),
            GirderFileIdToVolume(file['_id']),
            outputVolumePath
        ]

        # Result hooks
        # - Upload output files to output folder
        # - Provide source algorithm reference
        resultHooks = [
            GirderUploadVolumePathToFolder(outputVolumePath, outputFolder['_id'], upload_kwargs={
                'reference': json.dumps({_DANESFIELD_SOURCE_KEY: source})
            })
        ]

        job = docker_run.delay(
            image=_DANESFIELD_DOCKER_IMAGE,
            pull_image=False,
            container_args=containerArgs,
            girder_job_title='Fit DTM: %s' % file['name'],
            girder_result_hooks=resultHooks).job

        # Provide info for job event listeners
        job[_DANESFIELD_SOURCE_KEY] = source

        return Job().save(job)

    @access.user
    @filtermodel(model=Job)
    @autoDescribeRoute(
        Description('Generate a Digital Surface Model (DSM) from a point cloud.')
        .modelParam('itemId', 'The ID of the point cloud item.', model=Item, paramType='query',
                    level=AccessType.READ)
        .errorResponse()
        .errorResponse('Read access was denied on the item.', 403)
    )
    def generateDsm(self, item, params):
        """
        Generate a Digital Surface Model (DSM) from a point cloud.

        Requirements:
        - core3d/danesfield Docker image is available on host
        """
        # TODO: generate-dsm.py supports multiple point cloud files as input. To support
        # that workflow, this endpoint could accept a JSON list of file IDs.
        source = 'generate-dsm'
        file = self._fileFromItem(item)
        outputFolder = self._datasetsFolder()

        # Set output file name based on point cloud file
        dsmName = os.path.splitext(file['name'])[0] + '.tif'
        outputVolumePath = VolumePath(dsmName)

        # Docker container arguments
        containerArgs = [
            'python', 'danesfield/tools/generate-dsm.py',
            outputVolumePath,
            '--source_points',
            GirderFileIdToVolume(file['_id'])
        ]

        # Result hooks
        # - Upload output files to output folder
        # - Provide source algorithm reference
        resultHooks = [
            GirderUploadVolumePathToFolder(outputVolumePath, outputFolder['_id'], upload_kwargs={
                'reference': json.dumps({_DANESFIELD_SOURCE_KEY: source})
            })
        ]

        job = docker_run.delay(
            image=_DANESFIELD_DOCKER_IMAGE,
            pull_image=False,
            container_args=containerArgs,
            girder_job_title='Generate DSM: %s' % file['name'],
            girder_result_hooks=resultHooks).job

        # Provide info for job event listeners
        job[_DANESFIELD_SOURCE_KEY] = source

        return Job().save(job)

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
    )
    def generatePointCloud(self, imageItemIds, longitude, latitude, longitudeWidth, latitudeWidth,
                           params):
        """
        Generate a 3D point cloud from 2D images.

        Requirements:
        - p3d_gw Docker image is available on host
        - Host folder /mnt/GTOPO30 contains GTOPO 30 data
        """
        source = 'p3d'
        user = self.getCurrentUser()
        outputFolder = self._datasetsFolder()

        # Get file IDs from image item IDs
        imageFileIds = [
            self._fileFromItem(Item().load(itemId, level=AccessType.READ, user=user))['_id']
            for itemId in imageItemIds
        ]

        # Docker volumes
        volumes = [
            BindMountVolume(host_path='/mnt/GTOPO30', container_path='/P3D/GTOPO30', mode='ro')
        ]

        outputVolumePath = VolumePath('__output__')

        # Docker container arguments
        # TODO: Consider a solution where args are written to a file, in case of very long
        # command lines
        containerArgs = list(itertools.chain(
            [
                'python', '/P3D/RTN_distro/scripts/generate_point_cloud.pyc',
                '--out', outputVolumePath,
                '--longitude', str(longitude),
                '--latitude', str(latitude),
                '--longitudeWidth', str(longitudeWidth),
                '--latitudeWidth', str(latitudeWidth),
                '--firstProc', '0',
                '--threads', '1',
                '--images'
            ],
            [GirderFileIdToVolume(fileId) for fileId in imageFileIds],
        ))

        # Result hooks
        # - Upload output files to output folder
        # - Provide source algorithm reference
        resultHooks = [
            GirderUploadVolumePathToFolder(outputVolumePath, outputFolder['_id'], upload_kwargs={
                'reference': json.dumps({_DANESFIELD_SOURCE_KEY: source})
            })
        ]

        job = docker_run.delay(
            image=_P3D_DOCKER_IMAGE,
            pull_image=False,
            volumes=volumes,
            container_args=containerArgs,
            girder_job_title='Generate point cloud',
            girder_result_hooks=resultHooks).job

        # Provide info for job event listeners
        job[_DANESFIELD_SOURCE_KEY] = source

        return Job().save(job)
