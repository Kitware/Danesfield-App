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
    When a step completes, the handler associated with the step is executed.
    """
    def __init__(self):
        self._steps = {}

    def addHandler(self, stepName, handler):
        """
        Add handler to run when a step completes.

        The handler is a callable object that accepts the following parameters:
        - requestInfo: HTTP request info.
        - jobInfo: Danesfield job info.

        :param stepName: The name of the step.
        :type stepName: str (DanesfieldStep)
        :param handler: The step handler.
        :type handler: callable
        """
        self._steps[stepName] = handler

    def getHandler(self, stepName):
        """
        Get the handler associated with a step.

        :param stepName: The name of the step.
        :type stepName: str (DanesfieldStep)
        """
        return self._steps.get(stepName)
