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
    GirderFolderIdToVolume)

from .common import (
    addJobInfo,
    createDockerRunArguments,
    createGirderClient,
    createUploadMetadata)

from ..constants import DockerImage


def roofGeonExtraction(initWorkingSetName,
                       stepName,
                       requestInfo,
                       jobId,
                       outputFolder,
                       pointCloudFile,
                       dtmFile,
                       buildingMaskFile,
                       modelFolder,
                       modelFilePrefix):
    """
    Run a Girder Worker job to run Purdue and Columbia's roof geon
    extraction pipeline.

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
    :param pointCloudFile: Point cloud file document.
    :type pointCloudFile: dict
    :param dtmFile: DTM file document.
    :type dtmFile: dict
    :param buildingMaskFile: Building mask file document.
    :type buildingMaskFile: dict
    :param modelFolder: Model directory.
    :type modelFolder: dict
    :param modelFilePrefix: Model name prefix.
    :type modelFilePrefix: str
    :returns: Job document.
    """
    gc = createGirderClient(requestInfo)

    # Set output directory
    outputVolumePath = VolumePath('__output__')

    # Docker container arguments
    containerArgs = [
        'danesfield/tools/roof_geon_extraction.py',
        '--las', GirderFileIdToVolume(pointCloudFile['_id'], gc=gc),
        '--cls', GirderFileIdToVolume(buildingMaskFile['_id'], gc=gc),
        '--dtm', GirderFileIdToVolume(dtmFile['_id'], gc=gc),
        '--model_dir', GirderFolderIdToVolume(modelFolder['_id'], gc=gc),
        '--model_prefix', modelFilePrefix,
        '--output_dir', outputVolumePath
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
            jobTitle=('[%s] Roof geon extraction: %s' %
                      (initWorkingSetName, buildingMaskFile['name'])),
            jobType=stepName,
            user=requestInfo.user,
            resultHooks=resultHooks
        )
    )

    # Add info for job event listeners
    job = asyncResult.job
    job = addJobInfo(job, jobId=jobId, stepName=stepName)

    return job
