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
    GirderFileIdToVolume,
    GirderUploadVolumePathToFolder,
    GirderFolderIdToVolume)

from girder_worker.docker.transforms import TemporaryVolume

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
                   objFiles,
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
    :param objFiles: List of OBJ files.
    :type objFiles: list[dict]
    :param dtmFile: DTM file document.
    :type dtmFile: dict
    :returns: Job document.
    """
    gc = createGirderClient(requestInfo)

    # Set output path for DSM
    outputDSMVolumePath = VolumePath('buildings_to_dsm_DSM.tif')

    # Docker container arguments; FIXME: currently have to hack on the
    # individual GirderFileIdToVolume calls, so that we can get the
    # files we need in the same directory and pass into
    # buildings_to_dsm.  Could change buildings_to_dsm.py to take list
    # of files as a fix.
    containerArgsDSM = [
        'danesfield/tools/buildings_to_dsm.py',
        TemporaryVolume.default,
        GirderFileIdToVolume(dtmFile['_id'], gc=gc),
        outputDSMVolumePath,
        '&&',
        'echo'
    ]
    containerArgsDSM.extend([GirderFileIdToVolume(f['_id'], gc=gc)
                             for f in objFiles])

    # Set output path for CLS
    outputCLSVolumePath = VolumePath('buildings_to_dsm_CLS.tif')

    # Docker container arguments; FIXME: currently have to hack on the
    # individual GirderFileIdToVolume calls, so that we can get the
    # files we need in the same directory and pass into
    # buildings_to_dsm.  Could change buildings_to_dsm.py to take list
    # of files as a fix.
    containerArgsCLS = [
        'danesfield/tools/buildings_to_dsm.py',
        TemporaryVolume.default,
        GirderFileIdToVolume(dtmFile['_id'], gc=gc),
        outputCLSVolumePath,
        '--render_cls',
        '&&',
        'echo'
    ]
    containerArgsCLS.extend([GirderFileIdToVolume(f['_id'], gc=gc)
                             for f in objFiles])

    # Result hooks
    # - Upload output files to output folder
    # - Provide upload metadata
    upload_kwargs = createUploadMetadata(jobId, stepName)
    dsmResultHooks = [
        GirderUploadVolumePathToFolder(
            outputDSMVolumePath,
            outputFolder['_id'],
            upload_kwargs=upload_kwargs,
            gc=gc)
    ]
    clsResultHooks = [
        GirderUploadVolumePathToFolder(
            outputCLSVolumePath,
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
                resultHooks=dsmResultHooks
            )
        ),
        docker_run.s(
            **createDockerRunArguments(
                image=DockerImage.DANESFIELD,
                containerArgs=containerArgsCLS,
                jobTitle='Buildings to DSM: CLS generation',
                jobType=stepName,
                user=requestInfo.user,
                resultHooks=clsResultHooks
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
