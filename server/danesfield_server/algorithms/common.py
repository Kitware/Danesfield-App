#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
###############################################################################

import json
import re

from girder_jobs import Job

from girder_client import GirderClient

from ..constants import DanesfieldJobKey
from ..utilities import removeDuplicateCount


def createGirderClient(requestInfo):
    """Return new configured GirderClient instance."""
    gc = GirderClient(apiUrl=requestInfo.apiUrl)
    gc.token = requestInfo.token["_id"]
    return gc


def createUploadMetadata(jobId, stepName):
    """
    Return metadata to supply with uploaded files, including:
    - Job identifier
    - Step name

    :param jobId: Job ID.
    :type jobId: str
    :param stepName: The name of the step.
    :type stepName: str (DanesfieldStep)
    """
    upload_kwargs = {}
    if jobId is not None:
        upload_kwargs.update(
            {
                "reference": json.dumps(
                    {DanesfieldJobKey.ID: jobId, DanesfieldJobKey.STEP_NAME: stepName}
                )
            }
        )
    return upload_kwargs


def createDockerRunArguments(
    image, containerArgs, jobTitle, jobType, user, resultHooks=None
):
    """
    Return arguments to pass to docker_run Celery task.

    :param image: Docker image name.
    :type image: str
    :param containerArgs: Docker container arguments.
    :type containerArgs: list[str]
    :param jobTitle: Girder job title.
    :type jobTitle: str
    :param jobType: Girder job type.
    :type jobType: str
    :param user: User document.
    :type user: dict
    :param resultHooks: List of Girder Worker transforms.
    :type resultHooks: list
    :returns: dict
    """
    args = {
        "image": image,
        "pull_image": False,
        "container_args": containerArgs,
        "girder_job_title": jobTitle,
        "girder_job_type": jobType,
        "girder_user": user,
        # Force Python's stdout, stderr to be unbuffered. This ensures that the
        # job log is updated without waiting for a buffer to fill.
        "environment": ["PYTHONUNBUFFERED=1"],
    }
    if resultHooks is not None:
        args["girder_result_hooks"] = resultHooks

    return args


def addJobInfo(job, jobId, stepName, workingSetId):
    """
    Add common information to a job for use by job event listeners.
    This information allows the job event handler/workflow manager to
    process the job and continue running the workflow.

    :param job: Job document.
    :type job: dict
    :param jobId: Job ID.
    :type jobId: str
    :param stepName: The name of the step.
    :type stepName: str (DanesfieldStep)
    :returns: Updated job document.
    """
    if jobId is not None:
        job.update(
            {
                DanesfieldJobKey.ID: jobId,
                DanesfieldJobKey.STEP_NAME: stepName,
                DanesfieldJobKey.WORKINGSETID: workingSetId,
            }
        )
        job = Job().save(job)

    return job


def rpcFileMatchesImageFile(rpcFile, imageFile):
    """
    Return true if the RPC file corresponds to the image file.
    Matches are determined by file names.

    :param rpcFile: RPC file document.
    :type rpcFile: dict
    :param imageFile: Image file document.
    :type imageFile: dict
    """
    rpcBaseName = removeDuplicateCount(rpcFile["name"]).split(".")[0]
    # Remove suffix added to RPC files generated for MSI images
    result = re.match(r"^(?P<basename>.+)_\d+$", rpcBaseName)
    if result:
        rpcBaseName = result.group("basename")
    imageBaseName = imageFile["name"].split(".")[0]
    return rpcBaseName.endswith(imageBaseName)


def imagePrefix(imageFile):
    """
    Returns the image filename prefix for the given image file.

    :param imageFile: Image file document.
    :type imageFile: dict
    :returns: prefix string
    """
    match = re.match(
        r".*?(?P<prefix>[0-9]{2}[A-Z]{3}[0-9]{8})\-"
        "(?P<modality>P1BS|M1BS)\-"
        "(?P<trail>[0-9]{12}_[0-9]{2}_P[0-9]{3})",
        imageFile["name"],
        flags=re.IGNORECASE,
    )

    if match:
        return "%s-%s" % (match.group("prefix"), match.group("trail"))
    else:
        return None


def rpcPrefix(rpcFile):
    """
    Returns the RPC filename prefix for the given RPC file.

    :param rpcFile: RPC file document.
    :type rpcFile: dict
    :returns: prefix string
    """
    match = re.match(
        r".*?(?P<prefix>[0-9]{2}[A-Z]{3}[0-9]{8})\-"
        "(?P<modality>P1BS|M1BS)\-"
        "(?P<trail>[0-9]{12}_[0-9]{2}_P[0-9]{3})",
        rpcFile["name"],
        flags=re.IGNORECASE,
    )

    if match:
        return "%s-%s" % (match.group("prefix"), match.group("trail"))
    else:
        return None
