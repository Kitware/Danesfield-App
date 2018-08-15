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

from celery import group

from girder_worker.docker.tasks import docker_run
from girder_worker.docker.transforms import VolumePath
from girder_worker.docker.transforms.girder import (
    GirderFileIdToVolume, GirderUploadVolumePathToFolder)

from .common import addJobInfo, createGirderClient, createUploadMetadata
from ..constants import DockerImage
from ..utilities import getPrefix
from ..workflow import DanesfieldWorkflowException
from ..workflow_manager import DanesfieldWorkflowManager
from ..workflow_utilities import isMsiImage, isPanImage


def pansharpen(stepName, requestInfo, jobId, outputFolder, imageFiles):
    """
    Run Girder Worker jobs to pansharpen orthorectified images.

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
    :param imageFiles: List of orthorectified image files.
    :type imageFiles: list[dict]
    :returns: None
    """
    gc = createGirderClient(requestInfo)

    def createPansharpenTask(prefix, panImageFile, msiImageFile):
        # Set output file name based on prefix
        outputName = prefix + '_ortho_pansharpened.tif'
        outputVolumePath = VolumePath(outputName)

        # Docker container arguments
        containerArgs = [
            'gdal_pansharpen.py',
            # PAN image
            GirderFileIdToVolume(panImageFile['_id'], gc=gc),
            # MSI image
            GirderFileIdToVolume(msiImageFile['_id'], gc=gc),
            # Output image
            outputVolumePath
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

        return docker_run.s(
            image=DockerImage.DANESFIELD,
            pull_image=False,
            container_args=containerArgs,
            girder_job_title='Pansharpen: %s' % prefix,
            girder_job_type=stepName,
            girder_result_hooks=resultHooks,
            girder_user=requestInfo.user)

    # Group pairs of PAN and MSI images by prefix
    pairs = {}
    for imageFile in imageFiles:
        prefix = getPrefix(imageFile['name'])
        if prefix is None:
            raise DanesfieldWorkflowException(
                'Invalid orthorectified image file name: {}'.format(imageFile['name']),
                step=stepName)
        pairs.setdefault(prefix, {'pan': None, 'msi': None})
        if isPanImage(imageFile):
            pairs[prefix]['pan'] = imageFile
        elif isMsiImage(imageFile):
            pairs[prefix]['msi'] = imageFile
        else:
            raise DanesfieldWorkflowException(
                'Unrecognized image: {}'.format(imageFile['name']), step=stepName)

    # Ensure that both types of images exist for each prefix
    for files in pairs.values():
        panFile = files['pan']
        msiFile = files['msi']
        if not panFile or not msiFile:
            raise DanesfieldWorkflowException(
                'Corresponding PAN and MSI orthorectified images not found')

    # Run tasks in parallel using a group
    tasks = [
        createPansharpenTask(imagePrefix, files['pan'], files['msi'])
        for imagePrefix, files
        in pairs.items()
    ]
    groupResult = group(tasks).delay()

    DanesfieldWorkflowManager.instance().setGroupResult(jobId, stepName, groupResult)

    # Add info for job event listeners
    for result in groupResult.results:
        addJobInfo(result.job, jobId=jobId, stepName=stepName)
