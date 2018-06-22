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
    pass


class DanesfieldWorkflow(object):
    """
    Class to define the Danesfield workflow.
    When a job completes, the handler associated with the job source is executed.
    """
    def __init__(self):
        self._steps = {}

    def addHandler(self, source, handler):
        """
        Add handler to run when a job completes.

        Currently, the handler is a callable object that accepts the following
        parameters:
        - user: The user running the job.
        - apiUrl: The Girder API URL.
        - token: The user's token.
        - files: The list of files output from the job source.
        """
        # TODO: Improve handler interface: pack required data into an object
        self._steps[source] = handler

    def getHandler(self, source):
        """Get the handler associated with a job source."""
        return self._steps.get(source)
