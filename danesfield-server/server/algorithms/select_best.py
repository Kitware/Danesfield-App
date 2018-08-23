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
from girder_worker.docker.transforms.girder import GirderFileIdToVolume

from .common import addJobInfo, createDockerRunArguments, createGirderClient
from ..constants import DockerImage


def selectBest(stepName, requestInfo, jobId, outputFolder, imageFiles, dsmFile):
    """
    Run a Girder Worker job to select the best image pair.

    Requirements:
    - Danesfield Docker image is available on host

    :param stepName: The name of the step.
    :type stepName: str (DanesfieldStep)
    :param requestInfo: HTTP request and authorization info.
    :type requestInfo: RequestInfo
    :param jobId: Job ID.
    :type jobId: str
    :param outputFolder: Output folder document.
    :type outputFolder: dict
    :param imageFiles: List of image files.
    :type imageFiles: list[dict]
    :param file: DSM image file document.
    :type file: dict
    :returns: Job document.
    """
    gc = createGirderClient(requestInfo)

    # Docker container arguments
    containerArgs = list(itertools.chain(
        [
            'danesfield/tools/select_best.py',
            '--dsm', GirderFileIdToVolume(dsmFile['_id'], gc=gc)
        ],
        [
            GirderFileIdToVolume(imageFile['_id'], gc=gc)
            for imageFile in imageFiles
        ]
    ))

    asyncResult = docker_run.delay(
        **createDockerRunArguments(
            image=DockerImage.DANESFIELD,
            containerArgs=containerArgs,
            jobTitle='Select best',
            jobType=stepName,
            user=requestInfo.user
        )
    )

    # Add info for job event listeners
    job = asyncResult.job
    job = addJobInfo(job, jobId=jobId, stepName=stepName)

    return job
