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

from girder_worker.docker.tasks import docker_run
from girder_worker.docker.transforms import VolumePath
from girder_worker.docker.transforms.girder import (
    GirderFileIdToVolume, GirderUploadVolumePathToFolder)

from .common import addJobInfo, createGirderClient, createUploadMetadata
from ..constants import DockerImage


def segmentByHeight(stepName, requestInfo, jobId, outputFolder, dsmFile, dtmFile,
                    msiImageFile):
    """
    Run a Girder Worker job to segment buildings by comparing a DSM to a DTM.

    Requirements:
    - core3d/danesfield Docker image is available on host

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
    :returns: Job document.
    """
    gc = createGirderClient(requestInfo)

    # Set output file names
    # TODO: Danesfield master script hardcodes these without any prefix; do the same here
    thresholdOutputVolumePath = VolumePath('threshold_CLS.tif')
    ndviOutputVolumePath = VolumePath('ndvi.tif')

    # Docker container arguments
    containerArgs = [
        'danesfield/tools/segment_by_height.py',
        # DSM
        GirderFileIdToVolume(dsmFile['_id'], gc=gc),
        # DTM
        GirderFileIdToVolume(dtmFile['_id'], gc=gc),
        # Threshold output image
        thresholdOutputVolumePath,
        # MSI image
        '--msi', GirderFileIdToVolume(msiImageFile['_id'], gc=gc),
        # Normalized Difference Vegetation Index output image
        '--ndvi', ndviOutputVolumePath
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
        for outputVolumePath in [
            thresholdOutputVolumePath,
            ndviOutputVolumePath
        ]
    ]

    asyncResult = docker_run.delay(
        image=DockerImage.DANESFIELD,
        pull_image=False,
        container_args=containerArgs,
        girder_job_title='Segment by height: %s' % dsmFile['name'],
        girder_job_type=stepName,
        girder_result_hooks=resultHooks,
        girder_user=requestInfo.user)

    # Add info for job event listeners
    job = asyncResult.job
    job = addJobInfo(job, jobId=jobId, stepName=stepName)

    return job
