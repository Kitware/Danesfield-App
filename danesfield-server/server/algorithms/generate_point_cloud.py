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

from girder_worker.docker.tasks import docker_run
from girder_worker.docker.transforms import BindMountVolume, VolumePath
from girder_worker.docker.transforms.girder import (
    GirderFileIdToVolume, GirderUploadVolumePathToFolder)

from .common import addJobInfo, createDockerRunArguments, createGirderClient, createUploadMetadata
from ..constants import DockerImage


def generatePointCloud(stepName, requestInfo, jobId, outputFolder, imageFiles,
                       longitude, latitude, longitudeWidth, latitudeWidth):
    """
    Run a Girder Worker job to generate a 3D point cloud from 2D images.

    Requirements:
    - P3D Girder Worker Docker image is available on host
    - Host folder /mnt/GTOPO30 contains GTOPO 30 data

    :param stepName: The name of the step.
    :type stepName: str (DanesfieldStep)
    :param requestInfo: HTTP request and authorization info.
    :type requestInfo: RequestInfo
    :param jobId: Job ID.
    :type jobId: str
    :param outputFolder: Output folder document.
    :type outputFolder: dict
    :param imageFiles: List of input image files.
    :type imageFiles: list[dict]
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
    gc = createGirderClient(requestInfo)

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
            '--threads', '2',
            '--images'
        ],
        [GirderFileIdToVolume(imageFile['_id'], gc=gc) for imageFile in imageFiles],
    ))

    # Result hooks
    # - Upload output files to output folder
    # - Provide upload metadata
    upload_kwargs = createUploadMetadata(jobId, stepName)
    resultHooks = [
        GirderUploadVolumePathToFolder(
            outputVolumePath,
            outputFolder['_id'],
            upload_kwargs=upload_kwargs,
            gc=gc)
    ]

    asyncResult = docker_run.delay(
        volumes=volumes,
        **createDockerRunArguments(
            image=DockerImage.P3D,
            containerArgs=containerArgs,
            jobTitle='Generate point cloud',
            jobType=stepName,
            user=requestInfo.user,
            resultHooks=resultHooks
        )
    )

    # Add info for job event listeners
    job = asyncResult.job
    job = addJobInfo(job, jobId=jobId, stepName=stepName)

    return job