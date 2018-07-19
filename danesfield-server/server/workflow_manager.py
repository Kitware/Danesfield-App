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

import uuid

from girder import logprint

from .constants import DanesfieldStep
from .models.workingSet import WorkingSet
from .workflow import DanesfieldWorkflowException


class DanesfieldWorkflowManager(object):
    """
    Class to manage files and orchestrate steps in the Danesfield workflow.

    The class should generally be used through its singleton instance. The
    singleton should be initialized by configuring a DanesfieldWorkflow and
    setting it as the workflow property.

    Call initJob() to start a new job, then trigger the next step using advance().

    Handlers for workflow steps receive information about the original HTTP
    request and authorization, the job identifier, the initial working set and
    any working sets created during the workflow, and the folder in which to
    store output files.
    """
    _instance = None

    def __init__(self):
        # The workflow to run
        self.workflow = None

        # Data indexed by job ID
        self._jobInfo = {}

    @classmethod
    def instance(cls):
        """Access the singleton instance."""
        if cls._instance is None:
            cls._instance = DanesfieldWorkflowManager()
        return cls._instance

    def _createJobId(self):
        """Return new job identifier."""
        return uuid.uuid4().hex

    def _getJobInfo(self, jobId):
        """
        Get job info by ID. Raise an exception if the ID is invalid.

        :param jobId: Job identifier.
        :type jobId: str
        """
        jobInfo = self._jobInfo.get(jobId)
        if jobInfo is None:
            raise DanesfieldWorkflowException('Invalid job ID: \'{}\''.format(jobId))
        return jobInfo

    def initJob(self, workingSet, outputFolder, options):
        """
        Initialize a new job to run the workflow.

        :param workingSet: Source image working set.
        :type workingSet: dict
        :param outputFolder: Output folder document.
        :type outputFolder: dict
        :returns: Job identifier.
        :param options: Processing options.
        :type options: dict
        """
        if not self.workflow:
            raise DanesfieldWorkflowException('Workflow not configured')

        jobId = self._createJobId()
        self._jobInfo[jobId] = {
            # Working sets indexed by step name
            'workingSets': {
                DanesfieldStep.INIT: workingSet
            },
            # Files indexed by by step name
            'files': {},
            # Output folder
            'outputFolder': outputFolder,
            # Options
            'options': options if options is not None else {},
            # For composite steps, Celery GroupResult indexed by step name
            'groupResult': {}
        }

        logprint.info('DanesfieldWorkflowManager.initJob Job={} WorkingSet={}'.format(
            jobId, workingSet['_id']))

        return jobId

    def finalizeJob(self, jobId):
        """
        Finalize a job after completing the workflow.

        :param jobId: Job identifier.
        :type jobId: str
        """
        logprint.info('DanesfieldWorkflowManager.finalizeJob Job={}'.format(jobId))

        del self._jobInfo[jobId]

    def addFile(self, jobId, stepName, file):
        """
        Record a file created by a step.

        :param jobId: Identifier of job that created the file.
        :type jobId: str
        :param stepName: The name of the step that created the file.
        :type stepName: str (DanesfieldStep)
        :param file: File document.
        :type file: dict
        """
        logprint.info('DanesfieldWorkflowManager.addFile Job={} StepName={} File={}'.format(
            jobId, stepName, file['_id']))

        jobInfo = self._getJobInfo(jobId)
        jobInfo['files'].setdefault(stepName, []).append(file)

    def setGroupResult(self, jobId, stepName, groupResult):
        """
        Set the Celery GroupResult for a composite step.

        Composite steps run multiple Girder Worker jobs in parallel using a Celery group.
        When a single job completes, the GroupResult can be queried to check whether all
        jobs in the step have completed.

        :param jobId: Identifier of job that created the file.
        :type jobId: str
        :param stepName: The name of the step that created the file.
        :type stepName: str (DanesfieldStep)
        :param groupResult: Celery GroupResult.
        :type groupResult: celery.result.GroupResult
        """
        jobInfo = self._getJobInfo(jobId)
        jobInfo['groupResult'][stepName] = groupResult

    def getGroupResult(self, jobId, stepName):
        """
        Look up a Celery GroupResult for a composite step. Return None if no GroupResult is set
        for the step.
        """
        jobInfo = self._getJobInfo(jobId)
        return jobInfo['groupResult'].get(stepName)

    def advance(self, jobId, stepName, requestInfo):
        """
        Advance to the next step in the workflow.

        :param jobId: Identifier of the job running the workflow.
        :type jobId: str
        :param stepName: The name of the step that completed.
        :type stepName: str (DanesfieldStep)
        :param requestInfo: HTTP request and authorization info.
        :type requestInfo: RequestInfo
        """
        logprint.info('DanesfieldWorkflowManager.advance Job={} StepName={}'.format(
            jobId, stepName))

        jobInfo = self._getJobInfo(jobId)
        workingSets = jobInfo['workingSets']
        outputFolder = jobInfo['outputFolder']
        options = jobInfo['options']

        handler = self.workflow.getHandler(stepName)
        if handler is not None:
            handler(requestInfo, jobId, workingSets, outputFolder, options)

    def stepSucceeded(self, jobId, stepName):
        """
        Call when a step completes successfully.
        """
        logprint.info('DanesfieldWorkflowManager.stepSucceeded Job={} StepName={}'.format(
            jobId, stepName))

        jobInfo = self._getJobInfo(jobId)
        files = jobInfo['files'].get(stepName)
        if not files:
            return

        # Create working set containing files created by step
        workingSet = WorkingSet().save({
            'datasetIds': [file['itemId'] for file in files]
        })
        jobInfo['workingSets'][stepName] = workingSet

        # Remove data applicable only while step is running
        jobInfo['files'].pop(stepName, None)
        jobInfo['groupResult'].pop(stepName, None)

        logprint.info(
            'DanesfieldWorkflowManager.createdWorkingSet Job={} StepName={} WorkingSet={}'.format(
                jobId, stepName, workingSet['_id']))

    def stepFailed(self, jobId, stepName):
        """
        Call when a step fails or is canceled.
        """
        logprint.info('DanesfieldWorkflowManager.stepFailed Job={} StepName={}'.format(
            jobId, stepName))

        self._jobInfo.pop(jobId, None)
