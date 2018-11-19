#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
###############################################################################

import itertools

from girder_worker.docker.tasks import docker_run
from girder_worker.docker.transforms.girder import GirderFileIdToVolume

from .common import addJobInfo, createDockerRunArguments, createGirderClient
from ..constants import DockerImage


def selectBest(initWorkingSetName,
               stepName,
               requestInfo,
               jobId,
               outputFolder,
               imageFiles,
               dsmFile):
    """
    Run a Girder Worker job to select the best image pair.

    Requirements:
    - Danesfield Docker image is available on host

    :param initWorkingSetName: The name of the top-level working set.
    :type initWorkingSetName: str
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
            jobTitle='[%s] Select best' % initWorkingSetName,
            jobType=stepName,
            user=requestInfo.user
        )
    )

    # Add info for job event listeners
    job = asyncResult.job
    job = addJobInfo(job, jobId=jobId, stepName=stepName)

    return job
