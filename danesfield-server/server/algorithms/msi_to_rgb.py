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
from six.moves import zip

from girder_worker.docker.tasks import docker_run
from girder_worker.docker.transforms import VolumePath
from girder_worker.docker.transforms.girder import (
    GirderFileIdToVolume, GirderUploadVolumePathToFolder)

from .common import addJobInfo, createDockerRunArguments, createGirderClient, createUploadMetadata
from ..constants import DockerImage
from ..utilities import getPrefix
from ..workflow import DanesfieldWorkflowException
from ..workflow_manager import DanesfieldWorkflowManager


def msiToRgb(stepName, requestInfo, jobId, outputFolder, imageFiles, byte=None,
             alpha=None, rangePercentile=None):
    """
    Run Girder Worker jobs to convert multispectral (MSI) images to RGB.

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
    :param imageFiles: List of pansharpened MSI image files.
    :type imageFiles: list[dict]
    :param byte: Stretch intensity range and convert to a byte image.
    :type byte: bool
    :param alpha: Create an alpha channel instead of using zero as a no-value marker.
    :type alpha: bool
    :param rangePercentile: The percent of largest and smallest intensities to ignore when
        computing range for intensity scaling.
    :type rangePercentile: float
    :returns: None
    """
    gc = createGirderClient(requestInfo)

    def createConvertMsiToRgbTask(prefix, imageFile):
        # Set output file name based on prefix
        outputName = prefix + '_rgb_byte_image.tif'
        outputVolumePath = VolumePath(outputName)

        # Docker container arguments
        containerArgs = [
            'danesfield/tools/msi_to_rgb.py',
            # Pansharpened MSI image
            GirderFileIdToVolume(imageFile['_id'], gc=gc),
            # Output image
            outputVolumePath
        ]
        # Enable byte option by default
        if byte or byte is None:
            containerArgs.append('--byte')
        if alpha:
            containerArgs.append('--alpha')
        if rangePercentile is not None:
            containerArgs.extend(['--range-percentile', str(rangePercentile)])
        # TODO: Handle --big option (i.e. BIGTIFF)

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
            **createDockerRunArguments(
                image=DockerImage.DANESFIELD,
                containerArgs=containerArgs,
                jobTitle='Convert MSI to RGB: %s' % prefix,
                jobType=stepName,
                user=requestInfo.user,
                resultHooks=resultHooks
            )
        )

    # Get image file name prefixes for output file names
    prefixes = [
        getPrefix(imageFile['name'])
        for imageFile in imageFiles
    ]
    if not all(prefixes):
        raise DanesfieldWorkflowException('Invalid pansharpened image file name.', step=stepName)

    # Run tasks in parallel using a group
    tasks = [
        createConvertMsiToRgbTask(prefix, imageFile)
        for prefix, imageFile
        in zip(prefixes, imageFiles)
    ]
    groupResult = group(tasks).delay()

    DanesfieldWorkflowManager.instance().setGroupResult(jobId, stepName, groupResult)

    # Add info for job event listeners
    for result in groupResult.results:
        addJobInfo(result.job, jobId=jobId, stepName=stepName)
