#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
###############################################################################

import datetime
import json
import threading

from girder import events, logprint
from girder.models.folder import Folder
from girder.models.notification import Notification
from girder.models.user import User
from girder_jobs.models.job import Job
from girder_jobs.constants import JobStatus

from .constants import DanesfieldJobKey
from .models.workingSet import WorkingSet
from .workflow import DanesfieldWorkflowException
from .workflow_manager import DanesfieldWorkflowManager


# Lock for onJobUpdate()
_onJobUpdateLock = threading.RLock()


def cleanWorkingSetOutputFolder(job):
    """Clean a working set's existing output folder."""
    adminUser = User().getAdmins().next()
    workingSet = WorkingSet().load(job[DanesfieldJobKey.WORKINGSETID])
    output_folder = Folder().load(workingSet["output_folder_id"], user=adminUser)
    Folder().clean(output_folder)


def setWorkflowResultWorkingSets(job):
    """Create working sets from a workflow's output."""
    adminUser = User().getAdmins().next()
    workingSet = WorkingSet().load(job[DanesfieldJobKey.WORKINGSETID])
    output_folder = Folder().load(workingSet["output_folder_id"], user=adminUser)

    # Remove existing child working sets (except the necessary point cloud)
    childWorkingSets = [
        ws
        for ws in WorkingSet().find({"parentWorkingSetId": workingSet["_id"]})
        if "generate-point-cloud" not in ws["name"]
    ]
    for ws in childWorkingSets:
        WorkingSet().remove(ws)

    # For each folder in the output directory, create a working set
    for folder in Folder().childFolders(output_folder, "folder", user=adminUser):
        WorkingSet().createWorkingSet(
            name=f"{workingSet['name']}: {folder['name']}",
            parentWorkingSet=workingSet,
            datasetIds=[item["_id"] for item in Folder().childItems(folder)],
        )


def onFinalizeUpload(event):
    """
    Event handler for finalize upload event.

    When a Danesfield step uploads a file, add the file to the
    workflow manager to associate it with the job and workflow step.
    """
    upload = event.info["upload"]

    try:
        reference = json.loads(upload.get("reference"))
    except (TypeError, ValueError):
        return

    if not isinstance(reference, dict):
        return

    try:
        jobId = reference[DanesfieldJobKey.ID]
        stepName = reference[DanesfieldJobKey.STEP_NAME]
    except KeyError:
        return

    file = event.info["file"]
    DanesfieldWorkflowManager.instance().addFile(
        jobId=jobId, stepName=stepName, file=file
    )


def onJobUpdate(event):
    """
    Event handler for job update event.

    When a Danesfield job succeeds, advance the workflow.
    When a Danesfield job fails, remove its associated information
    from the workflow manager.
    """
    job = event.info["job"]
    params = event.info["params"]

    try:
        jobId = job[DanesfieldJobKey.ID]
        stepName = job[DanesfieldJobKey.STEP_NAME]
    except KeyError:
        return

    try:
        # FIXME: Sometimes status is unicode, not int
        status = int(params["status"])
    except (TypeError, KeyError, ValueError):
        return

    workflowManager = DanesfieldWorkflowManager.instance()

    with _onJobUpdateLock:
        # Handle composite steps
        if workflowManager.isCompositeStep(jobId, stepName):
            # Notify workflow manager when a job in a composite step completes
            if status in (JobStatus.SUCCESS, JobStatus.ERROR, JobStatus.CANCELED):
                workflowManager.compositeStepJobCompleted(jobId, stepName)
            # Skip processing until all jobs in a composite step have completed
            if not workflowManager.isCompositeStepComplete(jobId, stepName):
                return
            # Set overall status for composite step
            successful = workflowManager.isCompositeStepSuccessful(jobId, stepName)
            status = JobStatus.SUCCESS if successful else JobStatus.ERROR

        # Perform steps once job has been queued
        if status in (JobStatus.QUEUED, JobStatus.RUNNING):
            cleanWorkingSetOutputFolder(job)

        if status == JobStatus.SUCCESS:
            # Add standard output from job
            # TODO: Alternatively, could record job model ID and defer
            # log lookup
            # TODO: This currently doesn't support composite steps;
            # only the output
            # from the last job is saved
            job = Job().load(job["_id"], includeLog=True, force=True)
            workflowManager.addStandardOutput(
                jobId=jobId, stepName=stepName, output=job.get("log")
            )

            workflowManager.stepSucceeded(jobId=jobId, stepName=stepName)

            # For one-step imageless workflow results
            setWorkflowResultWorkingSets(job)

            # Advance workflow asynchronously to avoid affecting
            # finished job in case of error
            events.daemon.trigger(
                info={"jobId": jobId, "stepName": stepName, "userId": job["userId"]},
                callback=advanceWorkflow,
            )
        elif status in (JobStatus.CANCELED, JobStatus.ERROR):
            workflowManager.stepFailed(jobId=jobId, stepName=stepName)


def advanceWorkflow(event):
    """
    Advance to next step in workflow. Send a notification on error.
    """
    jobId = event.info["jobId"]
    stepName = event.info["stepName"]
    userId = event.info["userId"]

    user = User().load(userId, force=True, exc=True)

    try:
        DanesfieldWorkflowManager.instance().advance(jobId=jobId)
    except DanesfieldWorkflowException as e:
        logprint.warning(
            "advanceWorkflow: Error advancing workflow "
            "Job={} Step={} PreviousStep={} Message='{}'".format(
                jobId, e.step, stepName, str(e)
            )
        )

        # Create notification for workflow error
        Notification().createNotification(
            type="danesfield_workflow_error",
            data={"step": e.step or "", "previousStep": stepName, "message": str(e)},
            user=user,
            expires=datetime.datetime.utcnow() + datetime.timedelta(seconds=30),
        )
