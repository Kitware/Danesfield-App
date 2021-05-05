#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
###############################################################################

import os

from celery import group

from girder_worker.docker.tasks import docker_run
from girder_worker.docker.transforms import VolumePath
from girder_worker.docker.transforms.girder import (
    GirderFileIdToVolume,
    GirderUploadVolumePathToFolder,
)

from .common import (
    addJobInfo,
    createDockerRunArguments,
    createGirderClient,
    createUploadMetadata,
)
from ..constants import DockerImage
from ..workflow_manager import DanesfieldWorkflowManager


def orthorectify(
    initWorkingSetName,
    stepName,
    requestInfo,
    jobId,
    outputFolder,
    imageFiles,
    dsmFile,
    dtmFile,
    occlusionThreshold=None,
    denoiseRadius=None,
):
    """
    Run Girder Worker jobs to orthorectify source images.

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
    :param dsmFile: DSM file document.
    :type dsmFile: dict
    :param dtmFile: DTM file document.
    :type dtmFile: dict
    :param rpcFiles: List of RPC files.
    :type rpcFiles: list[dict]
    :param occlusionThreshold:
    :type occlusionThreshold: float
    :param denoiseRadius:
    :type denoiseRadius: float
    :returns: None
    """
    gc = createGirderClient(requestInfo)

    def createOrthorectifyTask(imageFile):
        # Set output file name based on input file name
        orthoName = os.path.splitext(imageFile["name"])[0] + "_ortho.tif"
        outputVolumePath = VolumePath(orthoName)

        # Docker container arguments
        containerArgs = [
            "python",
            "danesfield/tools/orthorectify.py",
            # Source image
            GirderFileIdToVolume(imageFile["_id"], gc=gc),
            # DSM
            GirderFileIdToVolume(dsmFile["_id"], gc=gc),
            # Destination image
            outputVolumePath,
            "--dtm",
            GirderFileIdToVolume(dtmFile["_id"], gc=gc),
        ]
        if occlusionThreshold is not None:
            containerArgs.extend(["--occlusion-thresh", str(occlusionThreshold)])
        if denoiseRadius is not None:
            containerArgs.extend(["--denoise-radius", str(denoiseRadius)])

        # Result hooks
        # - Upload output files to output folder
        # - Provide upload metadata
        upload_kwargs = createUploadMetadata(jobId, stepName)
        resultHooks = [
            GirderUploadVolumePathToFolder(
                outputVolumePath,
                outputFolder["_id"],
                upload_kwargs=upload_kwargs,
                gc=gc,
            )
        ]

        return docker_run.s(
            **createDockerRunArguments(
                image=DockerImage.DANESFIELD,
                containerArgs=containerArgs,
                jobTitle=(
                    "[%s] Orthorectify: %s" % (initWorkingSetName, imageFile["name"])
                ),
                jobType=stepName,
                user=requestInfo.user,
                resultHooks=resultHooks,
            )
        )

    # Run tasks in parallel using a group
    tasks = [createOrthorectifyTask(imageFile) for imageFile in imageFiles]
    groupResult = group(tasks).delay()

    DanesfieldWorkflowManager.instance().setGroupResult(jobId, stepName, groupResult)

    # Add info for job event listeners
    for result in groupResult.results:
        addJobInfo(result.job, jobId=jobId, stepName=stepName)
