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
import uuid

from girder.plugins.jobs.models.job import Job

from girder_client import GirderClient

from girder_worker.docker.tasks import docker_run
from girder_worker.docker.transforms import BindMountVolume, VolumePath
from girder_worker.docker.transforms.girder import (
    GirderFileIdToVolume, GirderUploadVolumePathToFolder)

from .constants import DanesfieldJobKey, DockerImage


def _createJobId():
    """Return new job identifier."""
    return uuid.uuid4().hex


def _createGirderClient(apiUrl, token):
    """Return new configured GirderClient instance."""
    gc = GirderClient(apiUrl=apiUrl)
    gc.token = token['_id']
    return gc


def fitDtm(user, apiUrl, token, trigger, file, outputFolder, iterations=100, tension=10):
    """
    Run a Girder Worker job to fit a Digital Terrain Model (DTM) to a Digital Surface Model (DSM).

    Requirements:
    - core3d/danesfield Docker image is available on host

    :param user: User document.
    :type user: dict
    :param apiUrl: API URL.
    :type apiUrl: str
    :param token: User's Girder token document.
    :type token: dict
    :param trigger: Whether to trigger the next step in the workflow.
    :type trigger: bool
    :param file: DSM image file document.
    :type file: dict
    :param outputFolder: Output folder document.
    :type outputFolder: dict
    :param iterations: The base number of iterations at the coarsest scale.
    :type iterations: int
    :param tension: Number of inner smoothing iterations.
    :type tension: int
    :returns: Job document.
    """
    source = 'fit-dtm'
    jobId = _createJobId()
    gc = _createGirderClient(apiUrl, token)

    # Set output file name based on input file name
    parts = os.path.splitext(file['name'])
    dsmName = '-dtm'.join(parts)
    outputVolumePath = VolumePath(dsmName)

    # Docker container arguments
    containerArgs = [
        'danesfield/tools/fit_dtm.py',
        '--num-iterations', str(iterations),
        '--tension', str(tension),
        GirderFileIdToVolume(file['_id'], gc=gc),
        outputVolumePath
    ]

    # Result hooks
    # - Upload output files to output folder
    # - Provide job identifier
    resultHooks = [
        GirderUploadVolumePathToFolder(
            outputVolumePath,
            outputFolder['_id'],
            upload_kwargs={
                'reference': json.dumps({
                    DanesfieldJobKey.ID: jobId
                })
            },
            gc=gc)
    ]

    asyncResult = docker_run.delay(
        image=DockerImage.DANESFIELD,
        pull_image=False,
        container_args=containerArgs,
        girder_job_title='Fit DTM: %s' % file['name'],
        girder_result_hooks=resultHooks,
        girder_user=user)

    # Provide info for job event listeners
    job = asyncResult.job
    job.update({
        DanesfieldJobKey.API_URL: apiUrl,
        DanesfieldJobKey.ID: jobId,
        DanesfieldJobKey.SOURCE: source,
        DanesfieldJobKey.TOKEN: token,
        DanesfieldJobKey.TRIGGER: trigger
    })

    return Job().save(job)


def generateDsm(user, apiUrl, token, trigger, file, outputFolder):
    """
    Run a Girder Worker job to generate a Digital Surface Model (DSM) from a point cloud.

    Requirements:
    - core3d/danesfield Docker image is available on host

    :param user: User document.
    :type user: dict
    :param apiUrl: API URL.
    :type apiUrl: str
    :param token: User's Girder token document.
    :type token: dict
    :param trigger: Whether to trigger the next step in the workflow.
    :type trigger: bool
    :param file: Point cloud file document.
    :type file: dict
    :param outputFolder: Output folder document.
    :type outputFolder: dict
    :returns: Job document.
    """
    source = 'generate-dsm'
    jobId = _createJobId()
    gc = _createGirderClient(apiUrl, token)

    # Set output file name based on point cloud file
    dsmName = os.path.splitext(file['name'])[0] + '.tif'
    outputVolumePath = VolumePath(dsmName)

    # Docker container arguments
    containerArgs = [
        'danesfield/tools/generate_dsm.py',
        outputVolumePath,
        '--source_points',
        GirderFileIdToVolume(file['_id'], gc=gc)
    ]

    # Result hooks
    # - Upload output files to output folder
    # - Provide job identifier
    resultHooks = [
        GirderUploadVolumePathToFolder(
            outputVolumePath,
            outputFolder['_id'],
            upload_kwargs={
                'reference': json.dumps({
                    DanesfieldJobKey.ID: jobId
                }),
            },
            gc=gc)
    ]

    asyncResult = docker_run.delay(
        image=DockerImage.DANESFIELD,
        pull_image=False,
        container_args=containerArgs,
        girder_job_title='Generate DSM: %s' % file['name'],
        girder_result_hooks=resultHooks,
        girder_user=user)

    # Provide info for job event listeners
    job = asyncResult.job
    job.update({
        DanesfieldJobKey.API_URL: apiUrl,
        DanesfieldJobKey.ID: jobId,
        DanesfieldJobKey.SOURCE: source,
        DanesfieldJobKey.TOKEN: token,
        DanesfieldJobKey.TRIGGER: trigger
    })

    return Job().save(job)


def generatePointCloud(user, apiUrl, token, trigger, imageFileIds, outputFolder, longitude,
                       latitude, longitudeWidth, latitudeWidth):
    """
    Run a Girder Worker job to generate a 3D point cloud from 2D images.

    Requirements:
    - p3d_gw Docker image is available on host
    - Host folder /mnt/GTOPO30 contains GTOPO 30 data

    :param user: User document.
    :type user: dict
    :param apiUrl: API URL.
    :type apiUrl: str
    :param token: User's Girder token document.
    :type token: dict
    :param trigger: Whether to trigger the next step in the workflow.
    :type trigger: bool
    :param imageFileIds: IDs of input image files.
    :type imageFileIds: list
    :param outputFolder: Output folder document.
    :type outputFolder: dict
    :param longitude:
    :type longitude:
    :param latitude:
    :type latitude:
    :param longitudeWidth:
    :type longitudeWidth:
    :param latitudeWidth:
    :type latitudeWidth:
    :returns: Job document.
    """
    source = 'p3d'
    jobId = _createJobId()
    gc = _createGirderClient(apiUrl, token)

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
        [GirderFileIdToVolume(fileId, gc=gc) for fileId in imageFileIds],
    ))

    # Result hooks
    # - Upload output files to output folder
    # - Provide job identifier
    resultHooks = [
        GirderUploadVolumePathToFolder(
            outputVolumePath,
            outputFolder['_id'],
            upload_kwargs={
                'reference': json.dumps({
                    DanesfieldJobKey.ID: jobId
                })
            },
            gc=gc)
    ]

    asyncResult = docker_run.delay(
        image=DockerImage.P3D,
        pull_image=False,
        volumes=volumes,
        container_args=containerArgs,
        girder_job_title='Generate point cloud',
        girder_result_hooks=resultHooks,
        girder_user=user)

    # Provide info for job event listeners
    job = asyncResult.job
    job.update({
        DanesfieldJobKey.API_URL: apiUrl,
        DanesfieldJobKey.ID: jobId,
        DanesfieldJobKey.SOURCE: source,
        DanesfieldJobKey.TOKEN: token,
        DanesfieldJobKey.TRIGGER: trigger
    })

    return Job().save(job)
