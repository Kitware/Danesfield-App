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

from .common import addJobInfo, createDockerRunArguments, createGirderClient, createUploadMetadata
from ..constants import DockerImage


def roofGeonExtraction(stepName, requestInfo, jobId, outputFolder, pointCloudFile, dtmFile,
                       buildingMaskFile):
    """
    Run a Girder Worker job to run Purdue's roof geon extraction.

    Requirements:
    - Danesfield Docker image is available on host

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
            jobTitle='Roof geon extraction: %s' % buildingMaskFile['name'],
            jobType=stepName,
            user=requestInfo.user,
            resultHooks=resultHooks
        )
    )

    # Add info for job event listeners
    job = asyncResult.job
    job = addJobInfo(job, jobId=jobId, stepName=stepName)

    return job
