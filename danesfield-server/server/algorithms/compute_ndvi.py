#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
###############################################################################



import itertools

from girder_worker.docker.tasks import docker_run
from girder_worker.docker.transforms import VolumePath
from girder_worker.docker.transforms.girder import (
    GirderFileIdToVolume,
    GirderUploadVolumePathToFolder)
from .common import (
    addJobInfo,
    createDockerRunArguments,
    createGirderClient,
    createUploadMetadata)
from ..constants import DockerImage


def computeNdvi(initWorkingSetName,
                stepName,
                requestInfo,
                jobId,
                outputFolder,
                imageFiles,
                outputNdviFilename):
    """
    Run a Girder Worker job to compute the NDVI from a set of images

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
    :param imageFiles: List of pansharpened image files.
    :type imageFiles: list[dict]
    :param outputNdviFilename: Filename for output NDVI
    :type outputNdviFilename: str
    :returns: Job document.
    """
    gc = createGirderClient(requestInfo)

    # Set output file names
    ndviOutputVolumePath = VolumePath(outputNdviFilename)

    # Docker container arguments
    containerArgs = list(itertools.chain(
        [
            'danesfield/tools/compute_ndvi.py',
        ],
        [
            GirderFileIdToVolume(imageFile['_id'], gc=gc)
            for imageFile in imageFiles
        ],
        [
            ndviOutputVolumePath
        ]))

    # Result hooks
    # - Upload output files to output folder
    # - Provide upload metadata
    upload_kwargs = createUploadMetadata(jobId, stepName)
    resultHooks = [
        GirderUploadVolumePathToFolder(
            ndviOutputVolumePath,
            outputFolder['_id'],
            upload_kwargs=upload_kwargs,
            gc=gc)
    ]

    asyncResult = docker_run.delay(
        **createDockerRunArguments(
            image=DockerImage.DANESFIELD,
            containerArgs=containerArgs,
            jobTitle='[%s] Compute NDVI' % initWorkingSetName,
            jobType=stepName,
            user=requestInfo.user,
            resultHooks=resultHooks
        )
    )

    # Add info for job event listeners
    job = asyncResult.job
    job = addJobInfo(job, jobId=jobId, stepName=stepName)

    return job
