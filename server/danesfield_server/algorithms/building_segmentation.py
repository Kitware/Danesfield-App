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
    GirderFileIdToVolume,
    GirderFolderIdToVolume,
    GirderUploadVolumePathToFolder,
)

from .common import (
    addJobInfo,
    createDockerRunArguments,
    createGirderClient,
    createUploadMetadata,
)
from ..constants import DockerImage


def buildingSegmentation(
    initWorkingSetName,
    stepName,
    requestInfo,
    jobId,
    outputFolder,
    dsmFile,
    dtmFile,
    msiImageFile,
    rgbImageFile,
    modelFolder,
    modelFilePrefix,
):
    """
    Run a Girder Worker job to segment buildings using Columbia
    building segmentation.

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
    :param dsmFile: DSM file document.
    :type dsmFile: dict
    :param dtmFile: DTM file document.
    :type dtmFile: dict
    :param msiImageFile: Pansharpened MSI image file document.
    :type msiImageFile: dict
    :param rgbImageFile: RGB image file document.
    :type rgbImageFile: dict
    :param modelFolder: Model folder document.
    :type modelFolder: dict
    :param modelFilePrefix: Model file prefix.
    :type modelFilePrefix: str
    :returns: Job document.
    """
    gc = createGirderClient(requestInfo)

    # Set output directory
    outputVolumePath = VolumePath(".")

    # Docker container arguments
    containerArgs = [
        "danesfield/tools/building_segmentation.py",
        "--rgb_image",
        GirderFileIdToVolume(rgbImageFile["_id"], gc=gc),
        "--msi_image",
        GirderFileIdToVolume(msiImageFile["_id"], gc=gc),
        "--dsm",
        GirderFileIdToVolume(dsmFile["_id"], gc=gc),
        "--dtm",
        GirderFileIdToVolume(dtmFile["_id"], gc=gc),
        "--model_dir",
        GirderFolderIdToVolume(modelFolder["_id"], gc=gc),
        "--model_prefix",
        modelFilePrefix,
        "--save_dir",
        outputVolumePath,
        "--output_tif",
    ]

    # Result hooks
    # - Upload output files to output folder
    # - Provide upload metadata
    upload_kwargs = createUploadMetadata(jobId, stepName)
    resultHooks = [
        GirderUploadVolumePathToFolder(
            outputVolumePath, outputFolder["_id"], upload_kwargs=upload_kwargs, gc=gc
        )
    ]

    asyncResult = docker_run.delay(
        **createDockerRunArguments(
            image=DockerImage.DANESFIELD,
            containerArgs=containerArgs,
            jobTitle=(
                "[%s] Building segmentation: %s" % (initWorkingSetName, dsmFile["name"])
            ),
            jobType=stepName,
            user=requestInfo.user,
            resultHooks=resultHooks,
        )
    )

    # Add info for job event listeners
    job = asyncResult.job
    job = addJobInfo(job, jobId=jobId, stepName=stepName)

    return job
