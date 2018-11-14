#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
###############################################################################



from girder_worker.docker.tasks import docker_run
from girder_worker.docker.transforms import VolumePath
from girder_worker.docker.transforms.girder import (
    GirderFileIdToVolume, GirderUploadVolumePathToFolder, GirderFolderIdToVolume)

from .common import addJobInfo, createDockerRunArguments, createGirderClient, createUploadMetadata
from ..constants import DockerImage


def getRoadVector(initWorkingSetName, stepName, requestInfo, jobId, outputFolder, left, bottom, right, top):
    """
    Run a Girder Worker job to segment buildings by comparing a DSM to a DTM.

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
    :param left: Longitude of left / westernmost side of bounding box
    :type left: float
    :param bottom: Latitude of bottom / southernmost side of bounding box
    :type bottom: float
    :param right: Longitude of right / easternmost side of bounding box
    :type right: float
    :param top: Latitude of top / northernmost side of bounding box
    :type top: float
    :returns: Job document.
    """
    gc = createGirderClient(requestInfo)

    # Set output file names
    outputVolumePath = VolumePath('__output__')

    # Docker container arguments
    containerArgs = [
        'danesfield/tools/get_road_vector.py',
        '--left', str(left),
        '--bottom', str(bottom),
        '--right', str(right),
        '--top', str(top),
        '--output-dir', outputVolumePath,
    ]

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
        **createDockerRunArguments(
            image=DockerImage.DANESFIELD,
            containerArgs=containerArgs,
            jobTitle='[%s] Get OSM road vector data' % initWorkingSetName,
            jobType=stepName,
            user=requestInfo.user,
            resultHooks=resultHooks
        )
    )

    # Add info for job event listeners
    job = asyncResult.job
    job = addJobInfo(job, jobId=jobId, stepName=stepName)

    return job
