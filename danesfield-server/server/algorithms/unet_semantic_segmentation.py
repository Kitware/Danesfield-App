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
    GirderFileIdToVolume, GirderUploadVolumePathToFolder)

from .common import (addJobInfo,
                     createDockerRunArguments,
                     createGirderClient,
                     createUploadMetadata)
from ..constants import DockerImage


def unetSemanticSegmentation(initWorkingSetName,
                             stepName,
                             requestInfo,
                             jobId,
                             outputFolder,
                             dsmFile,
                             dtmFile,
                             msiImageFile,
                             rgbImageFile,
                             configFile,
                             modelFile):
    """
    Run a Girder Worker job to segment buildings using UNet semantic
    segmentation.

    Requirements:
    - Danesfield Docker image is available on host

    :param initWorkingSetName: The name of the top-level working set.
    :type initWorkingSetName: strps
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
    :param configFile: Configuration file document.
    :type configFile: dict
    :param modelFile: Model file document.
    :type modelFile: dict
    :returns: Job document.
    """
    gc = createGirderClient(requestInfo)

    # Set output directory
    outputVolumePath = VolumePath('.')

    # Docker container arguments
    containerArgs = [
        'danesfield/tools/kwsemantic_segment.py',
        # Configuration file
        GirderFileIdToVolume(configFile['_id'], gc=gc),
        # Model file
        GirderFileIdToVolume(modelFile['_id'], gc=gc),
        # RGB image
        GirderFileIdToVolume(rgbImageFile['_id'], gc=gc),
        # DSM
        GirderFileIdToVolume(dsmFile['_id'], gc=gc),
        # DTM
        GirderFileIdToVolume(dtmFile['_id'], gc=gc),
        # MSI image
        GirderFileIdToVolume(msiImageFile['_id'], gc=gc),
        # Output directory
        outputVolumePath,
        # Output file prefix
        'semantic'
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
            jobTitle=('[%s] UNet semantic segmentation: %s' %
                      (initWorkingSetName, dsmFile['name'])),
            jobType=stepName,
            user=requestInfo.user,
            resultHooks=resultHooks
        )
    )

    # Add info for job event listeners
    job = asyncResult.job
    job = addJobInfo(job, jobId=jobId, stepName=stepName)

    return job
