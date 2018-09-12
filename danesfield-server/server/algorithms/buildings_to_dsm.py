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

from girder_worker.docker.tasks import docker_run
from girder_worker.docker.transforms import VolumePath
from girder_worker.docker.transforms.girder import (
    GirderFileIdToVolume,
    GirderUploadVolumePathToFolder,
    GirderFolderIdToVolume)

from .common import (
    addJobInfo,
    createDockerRunArguments,
    createGirderClient,
    createUploadMetadata)

from ..constants import DockerImage
from ..workflow_manager import DanesfieldWorkflowManager


def buildingsToDsm(stepName,
                   requestInfo,
                   jobId,
                   outputFolder,
                   objsFolder,
                   dtmFile):
    """
    Run a Girder Worker job to run Purdue and Columbia's roof geon
    extraction pipeline.

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
    :param objsFolder: Folder containing OBJ files.
    :type objsFolder: dict
    :param dtmFile: DTM file document.
    :type dtmFile: dict
    :returns: Job document.
    """
    gc = createGirderClient(requestInfo)

    # Set output directory
    outputVolumePath = VolumePath('__output__')

    # Docker container arguments
    containerArgsDSM = [
        'danesfield/tools/buildings_to_dsm.py',
        os.path.join(GirderFolderIdToVolume(objsFolder['_id'], gc=gc),
                     "output_obj"),
        GirderFileIdToVolume(dtmFile['_id'], gc=gc),
        os.path.join(outputVolumePath, "buildings_to_dsm_DSM.tif")
    ]

    containerArgsCLS = [
        'danesfield/tools/buildings_to_dsm.py',
        os.path.join(GirderFolderIdToVolume(objsFolder['_id'], gc=gc),
                     "output_obj"),
        GirderFileIdToVolume(dtmFile['_id'], gc=gc),
        os.path.join(outputVolumePath, "buildings_to_dsm_CLS.tif"),
        '--render_cls'
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

    tasks = [
        docker_run.s(
            **createDockerRunArguments(
                image=DockerImage.DANESFIELD,
                containerArgs=containerArgsDSM,
                jobTitle='Buildings to DSM: DSM generation',
                jobType=stepName,
                user=requestInfo.user,
                resultHooks=resultHooks
            )
        ),
        docker_run.s(
            **createDockerRunArguments(
                image=DockerImage.DANESFIELD,
                containerArgs=containerArgsCLS,
                jobTitle='Buildings to DSM: CLS generation',
                jobType=stepName,
                user=requestInfo.user,
                resultHooks=resultHooks
            )
        )
    ]

    groupResult = group(tasks).delay()

    DanesfieldWorkflowManager.instance().setGroupResult(jobId,
                                                        stepName,
                                                        groupResult)

    # Add info for job event listeners
    for result in groupResult.results:
        addJobInfo(result.job, jobId=jobId, stepName=stepName)
