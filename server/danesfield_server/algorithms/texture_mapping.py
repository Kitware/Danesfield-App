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
    GirderUploadVolumePathToFolder,
)

from .common import (
    addJobInfo,
    createDockerRunArguments,
    createGirderClient,
    createUploadMetadata,
)

from ..constants import DockerImage


def textureMapping(
    initWorkingSetName,
    stepName,
    requestInfo,
    jobId,
    outputFolder,
    objFiles,
    imageFiles,
    dsmFile,
    dtmFile,
):
    """
    Run a Girder Worker job to run texture mapping.

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
    :param objFiles: List of OBJ files.
    :type objFiles: list[dict]
    :param imageFiles: List of cropped and pansharpened image files.
    :type imageFiles: list[dict]
    :param dsmFile: DSM file document.
    :type dsmFile: dict
    :param dtmFile: DTM file document.
    :type dtmFile: dict
    :returns: Job document.
    """
    gc = createGirderClient(requestInfo)

    # Set output directory
    outputVolumePath = VolumePath("__output__")

    # Set output path for occlusion mesh
    occlusionMeshName = "xxxx.obj"
    occlusionMeshVolumePath = VolumePath(occlusionMeshName)

    containerArgs = [
        "danesfield/tools/texture_mapping.py",
        GirderFileIdToVolume(dsmFile["_id"], gc=gc),
        GirderFileIdToVolume(dtmFile["_id"], gc=gc),
        outputVolumePath,
        occlusionMeshVolumePath,
        "--crops",
    ]
    containerArgs.extend([GirderFileIdToVolume(f["_id"], gc=gc) for f in imageFiles])

    containerArgs.append("--buildings")
    containerArgs.extend([GirderFileIdToVolume(f["_id"], gc=gc) for f in objFiles])

    # Result hooks
    # - Upload output files to output folder
    # - Provide upload metadata
    upload_kwargs = createUploadMetadata(jobId, stepName)
    resultHooks = [
        GirderUploadVolumePathToFolder(
            outputVolumePath, outputFolder["_id"], upload_kwargs=upload_kwargs, gc=gc
        ),
        GirderUploadVolumePathToFolder(
            occlusionMeshVolumePath,
            outputFolder["_id"],
            upload_kwargs=upload_kwargs,
            gc=gc,
        ),
    ]

    asyncResult = docker_run.delay(
        **createDockerRunArguments(
            image=DockerImage.DANESFIELD,
            containerArgs=containerArgs,
            jobTitle="[%s] Texture mapping" % initWorkingSetName,
            jobType=stepName,
            user=requestInfo.user,
            resultHooks=resultHooks,
        )
    )

    # Add info for job event listeners
    job = asyncResult.job
    job = addJobInfo(job, jobId=jobId, stepName=stepName)

    return job
