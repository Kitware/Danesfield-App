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
