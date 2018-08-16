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

import threading
import uuid

from girder import logprint

from .constants import DanesfieldStep
from .job_info import JobInfo
from .models.workingSet import WorkingSet
from .workflow import DanesfieldWorkflowException


class DanesfieldWorkflowManager(object):
    """
    Class to manage files and orchestrate steps in the Danesfield workflow.

    The class should generally be used through its singleton instance. The
    singleton should be initialized by configuring a DanesfieldWorkflow and
    setting it as the workflow property.

    Call initJob() to start a new job, then advance the workflow to run the
    steps that are ready using advance().

    Handlers for workflow steps receive information about the original HTTP
    request and authorization, the job identifier, the initial working set and
    any working sets created during the workflow, the standard output for each step,
    the folder in which to store output files, and user-specified options.
    """
    _instance = None

    def __init__(self):
        # The workflow to run
        self.workflow = None

        # Data indexed by job ID
        self._jobData = {}

        # Lock
        self._lock = threading.RLock()

    @classmethod
    def instance(cls):
        """Access the singleton instance."""
        if cls._instance is None:
            cls._instance = DanesfieldWorkflowManager()
        return cls._instance

    def _createJobId(self):
        """Return new job identifier."""
        return uuid.uuid4().hex

    def _getJobData(self, jobId):
        """
        Get job data by ID. Raise an exception if the ID is invalid.

        :param jobId: Job identifier.
        :type jobId: str
        """
        jobData = self._jobData.get(jobId)
        if jobData is None:
            raise DanesfieldWorkflowException('Invalid job ID: \'{}\''.format(jobId))
        return jobData

    def initJob(self, requestInfo, workingSet, outputFolder, options):
        """
        Initialize a new job to run the workflow.

        :param requestInfo: HTTP request and authorization info.
        :type requestInfo: RequestInfo
        :param workingSet: Source image working set.
        :type workingSet: dict
        :param outputFolder: Output folder document.
        :type outputFolder: dict
        :returns: Job identifier.
        :param options: Processing options.
        :type options: dict
        """
        with self._lock:
            if not self.workflow:
                raise DanesfieldWorkflowException('Workflow not configured')

            jobId = self._createJobId()

            self._jobData[jobId] = {
                # Running steps
                'runningSteps': set(),
                # Completed steps
                'completedSteps': set(),
                # Request info
                'requestInfo': requestInfo,
                # Working sets indexed by step name
                'workingSets': {
                    DanesfieldStep.INIT: workingSet
                },
                # Files indexed by step name
                'files': {},
                # Standard output indexed by step name
                'standardOutput': {},
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
        with self._lock:
            logprint.info('DanesfieldWorkflowManager.finalizeJob Job={}'.format(jobId))

            del self._jobData[jobId]

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
        with self._lock:
            logprint.info('DanesfieldWorkflowManager.addFile Job={} StepName={} File={}'.format(
                jobId, stepName, file['_id']))

            jobData = self._getJobData(jobId)
            jobData['files'].setdefault(stepName, []).append(file)

    def addStandardOutput(self, jobId, stepName, output):
        """
        Record standard output from a step.

        :param jobId: Identifier of the job.
        :type jobId: str
        :param stepName: The name of the step to which the output belongs.
        :type stepName: str (DanesfieldStep)
        :param output: Standard output
        :type output: list[str]
        """
        with self._lock:
            logprint.info('DanesfieldWorkflowManager.addStandardOutput Job={} StepName={}'.format(
                jobId, stepName))

            jobData = self._getJobData(jobId)
            jobData['standardOutput'][stepName] = output

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
        with self._lock:
            jobData = self._getJobData(jobId)
            jobData['groupResult'][stepName] = groupResult

    def getGroupResult(self, jobId, stepName):
        """
        Look up a Celery GroupResult for a composite step. Return None if no GroupResult is set
        for the step.
        """
        with self._lock:
            jobData = self._getJobData(jobId)
            return jobData['groupResult'].get(stepName)

    def advance(self, jobId):
        """
        Advance the workflow.
        Runs all remaining steps that have their dependencies met.
        Finalizes the job if all steps are complete.

        :param jobId: Identifier of the job running the workflow.
        :type jobId: str
        """
        with self._lock:
            logprint.info('DanesfieldWorkflowManager.advance Job={}'.format(jobId))

            jobData = self._getJobData(jobId)

            incompleteSteps = [
                step
                for step in self.workflow.steps
                if step.name not in jobData['completedSteps']
            ]

            logprint.info('DanesfieldWorkflowManager.advance IncompleteSteps={}'.format(
                [step.name for step in incompleteSteps]
            ))

            runningSteps = [
                step
                for step in self.workflow.steps
                if step.name in jobData['runningSteps']
            ]

            logprint.info('DanesfieldWorkflowManager.advance RunningSteps={}'.format(
                [step.name for step in runningSteps]
            ))

            if not runningSteps and not incompleteSteps:
                self.finalizeJob(jobId)
                return

            readySteps = [
                step
                for step in incompleteSteps
                if step.name not in jobData['runningSteps'] and
                step.dependencies.issubset(jobData['completedSteps'])
            ]

            logprint.info('DanesfieldWorkflowManager.advance ReadySteps={}'.format(
                [step.name for step in readySteps]
            ))

            if not runningSteps and not readySteps and incompleteSteps:
                logprint.error('DanesfieldWorkflowManager.advance StuckSteps={}'.format(
                    [step.name for step in incompleteSteps]
                ))
                # TODO: More error notification/handling/clean up
                return

            jobInfo = JobInfo(
                jobId=jobId,
                requestInfo=jobData['requestInfo'],
                workingSets=jobData['workingSets'],
                standardOutput=jobData['standardOutput'],
                outputFolder=jobData['outputFolder'],
                options=jobData['options']
            )

            for step in readySteps:
                jobData['runningSteps'].add(step.name)
                step.run(jobInfo)

    def stepSucceeded(self, jobId, stepName):
        """
        Call when a step completes successfully.
        """
        with self._lock:
            logprint.info('DanesfieldWorkflowManager.stepSucceeded Job={} StepName={}'.format(
                jobId, stepName))

            jobData = self._getJobData(jobId)

            # Record that step completed
            jobData['runningSteps'].remove(stepName)
            jobData['completedSteps'].add(stepName)

            # Create working set containing files created by step
            files = jobData['files'].get(stepName)
            workingSet = None
            if files:
                initialWorkingSet = jobData['workingSets'][DanesfieldStep.INIT]
                workingSetName = '{}: {}'.format(initialWorkingSet['name'], stepName)
                datasetIds = [file['itemId'] for file in files]
                workingSet = WorkingSet().createWorkingSet(
                    name=workingSetName,
                    parentWorkingSet=initialWorkingSet,
                    datasetIds=datasetIds
                )
                jobData['workingSets'][stepName] = workingSet

            # Remove data applicable only while step is running
            jobData['files'].pop(stepName, None)
            jobData['groupResult'].pop(stepName, None)

            logprint.info(
                'DanesfieldWorkflowManager.createdWorkingSet Job={} StepName={} '
                'WorkingSet={}'.format(
                    jobId, stepName, workingSet['_id'] if workingSet is not None else None))

    def stepFailed(self, jobId, stepName):
        """
        Call when a step fails or is canceled.
        """
        with self._lock:
            logprint.info('DanesfieldWorkflowManager.stepFailed Job={} StepName={}'.format(
                jobId, stepName))

            self._jobData.pop(jobId, None)
