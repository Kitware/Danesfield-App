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
    GirderUploadVolumePathToFolder)
from .common import (
    addJobInfo,
    createDockerRunArguments,
    createGirderClient,
    createUploadMetadata)
from ..constants import DockerImage


def segmentByHeight(initWorkingSetName,
                    stepName,
                    requestInfo,
                    jobId,
                    outputFolder,
                    dsmFile,
                    dtmFile,
                    ndviFile,
                    roadVectorFile):
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
    :param dsmFile: DSM file document.
    :type dsmFile: dict
    :param dtmFile: DTM file document.
    :type dtmFile: dict
    :param ndviFile: NDVI file document.
    :type ndviFile: dict
    :param roadVectorFile: Road vector file.
    :type roadVectorFile: dict
    :returns: Job document.
    """
    gc = createGirderClient(requestInfo)

    # Set output file names
    # TODO: Danesfield master script hardcodes these without any
    # prefix; do the same here
    thresholdOutputVolumePath = VolumePath('threshold_CLS.tif')
    roadRasterOutputVolumePath = VolumePath('road_rasterized.tif')
    roadBridgeRasterOutputVolumePath = VolumePath('road_rasterized_bridge.tif')

    # Docker container arguments
    containerArgs = [
        'danesfield/tools/segment_by_height.py',
        # DSM
        GirderFileIdToVolume(dsmFile['_id'], gc=gc),
        # DTM
        GirderFileIdToVolume(dtmFile['_id'], gc=gc),
        # Threshold output image
        thresholdOutputVolumePath,
        # Normalized Difference Vegetation Index image
        '--input-ndvi', GirderFileIdToVolume(ndviFile['_id'], gc=gc),
        '--road-vector', GirderFileIdToVolume(roadVectorFile['_id'], gc=gc),
        '--road-rasterized', roadRasterOutputVolumePath,
        '--road-rasterized-bridge', roadBridgeRasterOutputVolumePath
    ]

    # Result hooks
    # - Upload output files to output folder
    # - Provide upload metadata
    upload_kwargs = createUploadMetadata(jobId, stepName)
    resultHooks = [
        GirderUploadVolumePathToFolder(
            thresholdOutputVolumePath,
            outputFolder['_id'],
            upload_kwargs=upload_kwargs,
            gc=gc)
    ]

    asyncResult = docker_run.delay(
        **createDockerRunArguments(
            image=DockerImage.DANESFIELD,
            containerArgs=containerArgs,
            jobTitle='[%s] Segment by height: %s' % (initWorkingSetName,
                                                     dsmFile['name']),
            jobType=stepName,
            user=requestInfo.user,
            resultHooks=resultHooks
        )
    )

    # Add info for job event listeners
    job = asyncResult.job
    job = addJobInfo(job, jobId=jobId, stepName=stepName)

    return job
