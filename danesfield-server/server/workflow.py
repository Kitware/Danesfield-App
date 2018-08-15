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


class DanesfieldWorkflowException(RuntimeError):
    """
    Exception raised when the workflow can't run as expected due to
    unexpected output from a job or from a misconfigured workflow.
    """
    def __init__(self, message, step=None):
        self.step = step
        super(DanesfieldWorkflowException, self).__init__(message)


class DanesfieldWorkflow(object):
    """
    Class to define the Danesfield workflow.
    """
    def __init__(self):
        self.steps = []

    def addStep(self, step):
        """
        Add a step to the workflow.

        :param step: The step to add.
        :type step: DanesfieldWorkflowStep
        """
        self.steps.append(step)


class DanesfieldWorkflowStep(object):
    """
    Class to define a step in the Danesfield workflow.
    """
    def __init__(self):
        self.dependencies = set()

    def addDependency(self, name):
        """
        Add a dependency to indicate that this step depends on the output of another step.
        """
        self.dependencies.add(name)

    def run(self, jobInfo):
        """
        Run the step. Subclasses must implement this method.

        :param jobInfo: The job context in which to run the step.
        :type jobInfo: JobInfo
        """
        raise NotImplementedError('Implement in subclass')
