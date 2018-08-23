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

import os

from celery import group
from six.moves import zip

from girder_worker.docker.tasks import docker_run
from girder_worker.docker.transforms import VolumePath
from girder_worker.docker.transforms.girder import (
    GirderFileIdToVolume, GirderUploadVolumePathToFolder)

from .common import addJobInfo, createGirderClient, createUploadMetadata, rpcFileMatchesImageFile
from ..constants import DockerImage
from ..workflow import DanesfieldWorkflowException
from ..workflow_manager import DanesfieldWorkflowManager


def orthorectify(stepName, requestInfo, jobId, outputFolder, imageFiles, dsmFile, dtmFile,
                 rpcFiles, occlusionThreshold=None, denoiseRadius=None):
    """
    Run Girder Worker jobs to orthorectify source images.

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

    def createOrthorectifyTask(imageFile, rpcFile):
        # Set output file name based on input file name
        orthoName = os.path.splitext(imageFile['name'])[0] + '_ortho.tif'
        outputVolumePath = VolumePath(orthoName)

        # Docker container arguments
        containerArgs = [
            'danesfield/tools/orthorectify.py',
            # Source image
            GirderFileIdToVolume(imageFile['_id'], gc=gc),
            # DSM
            GirderFileIdToVolume(dsmFile['_id'], gc=gc),
            # Destination image
            outputVolumePath,
            '--dtm', GirderFileIdToVolume(dtmFile['_id'], gc=gc),
            '--raytheon-rpc', GirderFileIdToVolume(rpcFile['_id'], gc=gc),
        ]
        if occlusionThreshold is not None:
            containerArgs.extend(['--occlusion-thresh', str(occlusionThreshold)])
        if denoiseRadius is not None:
            containerArgs.extend(['--denoise-radius', str(denoiseRadius)])

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

        return docker_run.s(
            image=DockerImage.DANESFIELD,
            pull_image=False,
            container_args=containerArgs,
            girder_job_title='Orthorectify: %s' % imageFile['name'],
            girder_job_type=stepName,
            girder_result_hooks=resultHooks,
            girder_user=requestInfo.user)

    # Find RPC file corresponding to each image, or None
    correspondingRpcFiles = [
        next(
            (
                rpcFile
                for rpcFile in rpcFiles
                if rpcFileMatchesImageFile(rpcFile, imageFile)
            ), None)
        for imageFile
        in imageFiles
    ]
    imagesMissingRpcFiles = [
        imageFile['name']
        for imageFile, rpcFile
        in zip(imageFiles, correspondingRpcFiles)
        if not rpcFile
    ]
    if imagesMissingRpcFiles:
        raise DanesfieldWorkflowException('Missing RPC files for images: {}'.format(
            imagesMissingRpcFiles), step=stepName)

    # Run tasks in parallel using a group
    tasks = [
        createOrthorectifyTask(imageFile, rpcFile)
        for imageFile, rpcFile
        in zip(imageFiles, correspondingRpcFiles)
    ]
    groupResult = group(tasks).delay()

    DanesfieldWorkflowManager.instance().setGroupResult(jobId, stepName, groupResult)

    # Add info for job event listeners
    for result in groupResult.results:
        addJobInfo(result.job, jobId=jobId, stepName=stepName)
