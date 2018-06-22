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

import json

from girder.models.user import User
from girder.plugins.jobs.constants import JobStatus

from .constants import DanesfieldJobKey
from .workflow_manager import DanesfieldWorkflowManager


def onFinalizeUpload(event):
    """
    Event handler for finalize upload event.

    When a Danesfield job uploads a file, add the file to the workflow manager to associate it
    with the job.
    """
    upload = event.info['upload']

    try:
        reference = json.loads(upload.get('reference'))
    except (TypeError, ValueError):
        return

    if not isinstance(reference, dict) or DanesfieldJobKey.ID not in reference:
        return

    jobId = reference[DanesfieldJobKey.ID]
    file = event.info['file']
    DanesfieldWorkflowManager.instance().addFile(jobId=jobId, file=file)


def onJobUpdate(event):
    """
    Event handler for job update event.

    When a Danesfield job succeeds, advance to the next stage of the workflow, when requested.
    When a Danesfield job fails, remove its associated information from the workflow manager.
    """
    job = event.info['job']
    params = event.info['params']

    if not all(key in job for key in (
            DanesfieldJobKey.API_URL,
            DanesfieldJobKey.ID,
            DanesfieldJobKey.SOURCE,
            DanesfieldJobKey.TOKEN,
            DanesfieldJobKey.TRIGGER)):
        return

    user = User().load(job['userId'], force=True, exc=True)
    apiUrl = job[DanesfieldJobKey.API_URL]
    jobId = job[DanesfieldJobKey.ID]
    source = job[DanesfieldJobKey.SOURCE]
    token = job[DanesfieldJobKey.TOKEN]
    trigger = job[DanesfieldJobKey.TRIGGER]

    try:
        # FIXME: Sometimes status is unicode, not int
        status = int(params['status'])
    except (TypeError, KeyError, ValueError):
        return

    if status == JobStatus.SUCCESS:
        if trigger:
            DanesfieldWorkflowManager.instance().advance(
                user=user, apiUrl=apiUrl, token=token, jobId=jobId, source=source)
        else:
            DanesfieldWorkflowManager.instance().jobSucceeded(jobId=jobId)
    elif status in (JobStatus.CANCELED, JobStatus.ERROR):
        DanesfieldWorkflowManager.instance().jobFailed(jobId=jobId)
