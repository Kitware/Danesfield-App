#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
###############################################################################

from celery import group

from girder_worker.docker.tasks import docker_run
from girder_worker.docker.transforms import VolumePath
from girder_worker.docker.transforms.girder import (
    GirderFileIdToVolume,
    GirderUploadVolumePathToFolder)

from .common import (
    addJobInfo,
    createDockerRunArguments,
    createGirderClient,
    createUploadMetadata)

from ..constants import DockerImage
from ..workflow_manager import DanesfieldWorkflowManager


def buildingsToDsm(initWorkingSetName,
                   stepName,
                   requestInfo,
                   jobId,
                   outputFolder,
                   objFiles,
                   dtmFile,
                   outputPrefix):
    """
    Run a Girder Worker job to run Purdue and Columbia's roof geon
    extraction pipeline.

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
    :param objFiles: List of OBJ files.
    :type objFiles: list[dict]
    :param dtmFile: DTM file document.
    :type dtmFile: dict
    :param outputPrefix: The prefix of the output file name.
    :type outputPrefix: str
    :returns: Job document.
    """
    gc = createGirderClient(requestInfo)

    # Set output path for DSM
    outputDSMName = outputPrefix + '_rendered_DSM.tif'
    outputDSMVolumePath = VolumePath(outputDSMName)

    containerArgsDSM = [
        'danesfield/tools/buildings_to_dsm.py',
        GirderFileIdToVolume(dtmFile['_id'], gc=gc),
        outputDSMVolumePath,
        '--input_obj_paths'
    ]
    containerArgsDSM.extend([GirderFileIdToVolume(f['_id'], gc=gc)
                             for f in objFiles])

    # Set output path for CLS
    outputCLSName = outputPrefix + '_rendered_CLS.tif'
    outputCLSVolumePath = VolumePath(outputCLSName)

    containerArgsCLS = [
        'danesfield/tools/buildings_to_dsm.py',
        GirderFileIdToVolume(dtmFile['_id'], gc=gc),
        outputCLSVolumePath,
        '--render_cls',
        '--input_obj_paths'
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
                jobTitle=('[%s] Buildings to DSM: DSM generation' %
                          initWorkingSetName),
                jobType=stepName,
                user=requestInfo.user,
                resultHooks=dsmResultHooks
            )
        ),
        docker_run.s(
            **createDockerRunArguments(
                image=DockerImage.DANESFIELD,
                containerArgs=containerArgsCLS,
                jobTitle=('[%s] Buildings to DSM: CLS generation' %
                          initWorkingSetName),
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
