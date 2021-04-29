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
)

from .common import (
    addJobInfo,
    createDockerRunArguments,
    createGirderClient,
    createUploadMetadata,
)
from ..constants import DockerImage


def fitDtm(
    initWorkingSetName,
    stepName,
    requestInfo,
    jobId,
    outputFolder,
    dsmFile,
    outputPrefix,
    iterations=None,
    tension=None,
):
    """
    Run a Girder Worker job to fit a Digital Terrain Model (DTM) to a
    Digital Surface Model (DSM).

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
    :param dsmFile: DSM image file document.
    :type dsmFile: dict
    :param outputPrefix: The prefix of the output file name.
    :type outputPrefix: str
    :param iterations: The base number of iterations at the coarsest scale.
    :type iterations: int
    :param tension: Number of inner smoothing iterations.
    :type tension: int
    :returns: Job document.
    """
    gc = createGirderClient(requestInfo)

    # Set output file name based on input file name
    dtmName = outputPrefix + "_DTM.tif"
    outputVolumePath = VolumePath(dtmName)

    # Docker container arguments
    containerArgs = [
        "python",
        "danesfield/tools/fit_dtm.py",
        GirderFileIdToVolume(dsmFile["_id"], gc=gc),
        outputVolumePath,
    ]
    if iterations is not None:
        containerArgs.extend(["--num-iterations", str(iterations)])
    if tension is not None:
        containerArgs.extend(["--tension", str(tension)])

    # Result hooks
    # - Upload output files to output folder
    # - Provide upload metadata
    upload_kwargs = createUploadMetadata(jobId, stepName)
    resultHooks = [
        GirderUploadVolumePathToFolder(
            outputVolumePath, outputFolder["_id"], upload_kwargs=upload_kwargs, gc=gc
        )
    ]

    asyncResult = docker_run.delay(
        **createDockerRunArguments(
            image=DockerImage.DANESFIELD,
            containerArgs=containerArgs,
            jobTitle=("[%s] Fit DTM: %s" % (initWorkingSetName, dsmFile["name"])),
            jobType=stepName,
            user=requestInfo.user,
            resultHooks=resultHooks,
        )
    )

    # Add info for job event listeners
    job = asyncResult.job
    job = addJobInfo(job, jobId=jobId, stepName=stepName)

    return job
