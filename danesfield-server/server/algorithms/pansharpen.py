#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
###############################################################################

from celery import group

from girder import logprint
from girder_worker.docker.tasks import docker_run
from girder_worker.docker.transforms import VolumePath
from girder_worker.docker.transforms.girder import (
    GirderFileIdToVolume, GirderUploadVolumePathToFolder)

from .common import (addJobInfo,
                     createDockerRunArguments,
                     createGirderClient,
                     createUploadMetadata)
from ..constants import DockerImage
from ..utilities import getPrefix
from ..workflow import DanesfieldWorkflowException
from ..workflow_manager import DanesfieldWorkflowManager
from ..workflow_utilities import isMsiImage, isPanImage


def pansharpen(initWorkingSetName,
               stepName,
               requestInfo,
               jobId,
               outputFolder,
               imageFiles):
    """
    Run Girder Worker jobs to pansharpen orthorectified images.

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
            **createDockerRunArguments(
                image=DockerImage.DANESFIELD,
                containerArgs=containerArgs,
                jobTitle='[%s] Pansharpen: %s' % (initWorkingSetName, prefix),
                jobType=stepName,
                user=requestInfo.user,
                resultHooks=resultHooks
            )
        )

    # Group pairs of PAN and MSI images by prefix
    pairs = {}
    for imageFile in imageFiles:
        prefix = getPrefix(imageFile['name'])
        if prefix is None:
            raise DanesfieldWorkflowException(
                'Invalid orthorectified image file name: {}'.
                format(imageFile['name']),
                step=stepName)
        pairs.setdefault(prefix, {'pan': None, 'msi': None})
        if isPanImage(imageFile):
            pairs[prefix]['pan'] = imageFile
        elif isMsiImage(imageFile):
            pairs[prefix]['msi'] = imageFile
        else:
            raise DanesfieldWorkflowException(
                'Unrecognized image: {}'.
                format(imageFile['name']), step=stepName)

    # Ensure that both types of images exist for each prefix
    # Logging a warning for now and skipping rather than treating this
    # as an exception
    for prefix, files in pairs.items():
        panFile = files['pan']
        msiFile = files['msi']
        if not panFile or not msiFile:
            logprint.info("Step: {} -- Warning: Don't have both PAN and MSI \
images for: {}".format(stepName, prefix))
            # raise DanesfieldWorkflowException(
            #     'Corresponding PAN and MSI orthorectified images not found')

    # Run tasks in parallel using a group
    tasks = [
        createPansharpenTask(imagePrefix, files['pan'], files['msi'])
        for imagePrefix, files
        in pairs.items()
        if files['pan'] and files['msi']
    ]
    groupResult = group(tasks).delay()

    DanesfieldWorkflowManager.instance().setGroupResult(jobId,
                                                        stepName,
                                                        groupResult)

    # Add info for job event listeners
    for result in groupResult.results:
        addJobInfo(result.job, jobId=jobId, stepName=stepName)
