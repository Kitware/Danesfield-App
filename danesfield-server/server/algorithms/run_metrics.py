#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
###############################################################################



from girder_worker.docker.tasks import docker_run
from girder_worker.docker.transforms import VolumePath
from girder_worker.docker.transforms.girder import (
    GirderFileIdToVolume,
    GirderUploadVolumePathToFolder,
    GirderFolderIdToVolume)

from .common import addJobInfo, createDockerRunArguments, createGirderClient, createUploadMetadata
from ..constants import DockerImage


def runMetrics(initWorkingSetName,
               stepName,
               requestInfo,
               jobId,
               outputFolder,
               referenceFolder,
               referencePrefix,
               dtmFile,
               dsmFile,
               clsFile,
               mtlFile):
    """
    Run a Girder Worker job to compute metrics on output files.

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
    :param referenceFolder: Reference directory.
    :type referenceFolder: dict
    :param referencePrefix: Reference file prefix.
    :type referencePrefix: str
    :param dtmFile: DTM file document.
    :type dtmFile: dict
    :param dsmFile: DSM file document.
    :type dsmFile: dict
    :param clsFile: CLS file document.
    :type clsFile: dict
    :param mtlFile: MTL file document.
    :type mtlFile: dict
    :returns: Job document.
    """
    gc = createGirderClient(requestInfo)

    if referencePrefix == "STANDARD":
        # We know that there's no reference data with this selection
        containerArgs = [
            'echo',
            'No ground truth selected for scoring']

        asyncResult = docker_run.delay(
            **createDockerRunArguments(
                image=DockerImage.DANESFIELD,
                containerArgs=containerArgs,
                jobTitle='[%s] Run metrics' % initWorkingSetName,
                jobType=stepName,
                user=requestInfo.user
            )
        )
    else:
        # Otherwise we assume the reference data exists, and try to
        # run the metrics
        outputVolumePath = VolumePath('__output__')

        # Docker container arguments
        containerArgs = [
            'danesfield/tools/run_metrics.py',
            '--output-dir', outputVolumePath,
            '--ref-dir', GirderFolderIdToVolume(referenceFolder['_id'], gc=gc),
            '--ref-prefix', referencePrefix,
            '--dsm', GirderFileIdToVolume(dsmFile['_id'], gc=gc),
            '--cls', GirderFileIdToVolume(clsFile['_id'], gc=gc),
            '--mtl', GirderFileIdToVolume(mtlFile['_id'], gc=gc),
            '--dtm', GirderFileIdToVolume(dtmFile['_id'], gc=gc)
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
                jobTitle='[%s] Run metrics' % initWorkingSetName,
                jobType=stepName,
                user=requestInfo.user,
                resultHooks=resultHooks
            )
        )

    # Add info for job event listeners
    job = asyncResult.job
    job = addJobInfo(job, jobId=jobId, stepName=stepName)

    return job
