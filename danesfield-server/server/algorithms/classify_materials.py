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

import itertools

from six.moves import zip

from girder_worker.docker.tasks import docker_run
from girder_worker.docker.transforms import VolumePath
from girder_worker.docker.transforms.girder import (
    GirderFileIdToVolume, GirderUploadVolumePathToFolder)

from .common import addJobInfo, createGirderClient, createUploadMetadata
from ..constants import DockerImage
from ..utilities import getPrefix
from ..workflow import DanesfieldWorkflowException


def classifyMaterials(stepName, requestInfo, jobId, outputFolder, imageFiles,
                      metadataFiles, modelFile, cuda=None, batchSize=None):
    """
    Run a Girder Worker job to classify materials in an orthorectified image.

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
    :param imageFiles: List of orthorectified MSI image files.
    :type imageFiles: list[dict]
    :param metadataFiles: List of MSI-source NITF metadata files.
    :type metadataFiles: list[dict]
    :param modelFile: Model file document.
    :type modelFile: dict
    :param cuda: Enable CUDA.
    :type cuda: bool
    :param batchSize: Number of pixels classified at a time.
    :type batchSize: int
    :returns: Job document.
    """
    gc = createGirderClient(requestInfo)

    outputVolumePath = VolumePath('.')

    # Find NITF metadata file corresponding to each image, or None
    correspondingMetadataFiles = [
        next(
            (
                metadataFile
                for metadataFile in metadataFiles
                if getPrefix(metadataFile['name']) == getPrefix(imageFile['name'])
            ), None)
        for imageFile in imageFiles
    ]
    imagesMissingMetadataFiles = [
        imageFile['name']
        for imageFile, metadataFile
        in zip(imageFiles, correspondingMetadataFiles)
        if not metadataFile
    ]
    if imagesMissingMetadataFiles:
        raise DanesfieldWorkflowException('Missing NITF metadata files for images: {}'.format(
            imagesMissingMetadataFiles), step=stepName)

    # Docker container arguments
    containerArgs = list(itertools.chain(
        [
            'danesfield/tools/material_classifier.py',
            '--model_path', GirderFileIdToVolume(modelFile['_id'], gc=gc),
            '--output_dir', outputVolumePath,
            '--image_paths'
        ],
        [
            GirderFileIdToVolume(imageFile['_id'], gc=gc)
            for imageFile in imageFiles
        ],
        [
            '--info_paths'
        ],
        [
            GirderFileIdToVolume(metadataFile['_id'], gc=gc)
            for metadataFile in correspondingMetadataFiles
        ]
    ))
    if cuda:
        containerArgs.append('--cuda')
    if batchSize is not None:
        containerArgs.extend(['--batch_size', str(batchSize)])

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
        image=DockerImage.DANESFIELD,
        pull_image=False,
        container_args=containerArgs,
        girder_job_title='Classify materials',
        girder_job_type=stepName,
        girder_result_hooks=resultHooks,
        girder_user=requestInfo.user)

    # Add info for job event listeners
    job = asyncResult.job
    job = addJobInfo(job, jobId=jobId, stepName=stepName)

    return job
