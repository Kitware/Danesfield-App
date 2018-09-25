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

from .common import (
    addJobInfo,
    createDockerRunArguments,
    createGirderClient,
    createUploadMetadata,
    imagePrefix,
    rpcPrefix)
from ..constants import DockerImage
from ..workflow_manager import DanesfieldWorkflowManager


def cropAndPansharpen(initWorkingSetName,
                      stepName,
                      requestInfo,
                      jobId,
                      outputFolder,
                      dsmFile,
                      msiImageFiles,
                      panImageFiles,
                      msiRpcFiles,
                      panRpcFiles,
                      rpcFiles):
    """
    Run a Girder Worker job to crop and pansharpen images for texture mapping.

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
    :param msiImageFiles: List of MSI image files.
    :type msiImageFiles: list[dict]
    :param panImageFiles: List of PAN image files.
    :type panImageFiles: list[dict]
    :param msiRpcFiles: List of MSI RPC files.
    :type msiRpcFiles: list[dict]
    :param panRpcFiles: List of PAN RPC files.
    :type panRpcFiles: list[dict]
    :returns: Job document.
    """
    gc = createGirderClient(requestInfo)

    def createCropAndPansharpenTask(prefix,
                                    msiImageFile,
                                    panImageFile,
                                    msiRpcFile=None,
                                    panRpcFile=None):
        # Set output directory
        outputVolumePath = VolumePath('__output__')

        containerArgs = [
            'danesfield/tools/crop_and_pansharpen.py',
            GirderFileIdToVolume(dsmFile['_id'], gc=gc),
            outputVolumePath,
            '--pan',
            GirderFileIdToVolume(panImageFile['_id'], gc=gc)
        ]
        if panRpcFile is not None:
            containerArgs.append(GirderFileIdToVolume(panRpcFile['_id'],
                                                      gc=gc))

        containerArgs.extend([
            '--msi',
            GirderFileIdToVolume(msiImageFile['_id'], gc=gc)
        ])
        if msiRpcFile is not None:
            containerArgs.append(GirderFileIdToVolume(msiRpcFile['_id'],
                                                      gc=gc))

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
                jobTitle='[%s] Crop and pansharpen: %s' % (initWorkingSetName,
                                                           prefix),
                jobType=stepName,
                user=requestInfo.user,
                resultHooks=resultHooks
            )
        )

    collection = {}
    for imageFile in msiImageFiles:
        prefix = imagePrefix(imageFile)
        if prefix is not None:
            if prefix not in collection:
                collection[prefix] = {}

            collection[prefix]["msi"] = imageFile

    for imageFile in panImageFiles:
        prefix = imagePrefix(imageFile)
        if prefix is not None:
            if prefix not in collection:
                collection[prefix] = {}

            collection[prefix]["pan"] = imageFile

    for rpcFile in msiRpcFiles:
        prefix = rpcPrefix(rpcFile)
        if prefix is not None:
            if prefix not in collection:
                collection[prefix] = {}

            collection[prefix]["msi_rpc"] = rpcFile

    for rpcFile in panRpcFiles:
        prefix = rpcPrefix(rpcFile)
        if prefix is not None:
            if prefix not in collection:
                collection[prefix] = {}

            collection[prefix]["pan_rpc"] = rpcFile

    tasks = []
    for prefix, files in collection.items():
        # Skip if we don't have both MSI and PAN images
        if "msi" in files and "pan" in files:
            tasks.append(
                createCropAndPansharpenTask(prefix,
                                            files["msi"],
                                            files["pan"],
                                            files.get("msi_rpc"),
                                            files.get("pan_rpc")))

    groupResult = group(tasks).delay()

    DanesfieldWorkflowManager.instance().setGroupResult(jobId,
                                                        stepName,
                                                        groupResult)

    # Add info for job event listeners
    for result in groupResult.results:
        addJobInfo(result.job, jobId=jobId, stepName=stepName)
