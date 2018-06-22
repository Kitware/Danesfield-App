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

from .workflow import DanesfieldWorkflowException


class DanesfieldWorkflowManager(object):
    """
    Class to manage data and orchestrate jobs in the Danesfield workflow.

    In this first draft, this class assumes that the jobs run serially and
    each job depends only on the output of the previous job. That will
    likely have to change. Because of this assumption, the class currently
    clears the data associated with a job when the job ends. Eventually
    this manager should maintain data for every job run during a workflow
    until the entire workflow completes. Each job should be able to look up
    the output from any previous job.
    """
    _instance = None

    def __init__(self):
        self.workflow = None
        self._outputs = {}

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = DanesfieldWorkflowManager()
        return cls._instance

    def addFile(self, jobId, file):
        """
        Indicate that a job created a file.
        """
        self._outputs.setdefault(jobId, []).append(file)

    def advance(self, user, apiUrl, token, jobId, source):
        """
        Advance to the next job in the workflow.
        The new job receives the files created in the previous job.
        """
        if not self.workflow:
            raise DanesfieldWorkflowException('Workflow not configured')

        files = self._outputs.pop(jobId)

        handler = self.workflow.getHandler(source)
        if handler is not None:
            handler(user, apiUrl, token, files)

    def jobSucceeded(self, jobId):
        """
        Call when a job completes successfully.
        """
        del self._outputs[jobId]

    def jobFailed(self, jobId):
        """
        Call when a job fails or is canceled.
        """
        del self._outputs[jobId]
