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


class JobInfo:
    """
    Class to store Danesfield job information.
    A job is an instance of a running workflow.
    """
    def __init__(self, jobId, workingSets, standardOutput, outputFolder, options):
        """
        :param jobId: Identifier of Danesfield job.
        :type jobId: str
        :param workingSets: The initial working set and working sets created during the workflow.
            Indexed by step name.
        :type workingSets: dict
        :param standardOutput: The standard output of each step. Lists of strings, indexed by
            step name.
        :type standardOutput: dict
        :param outputFolder: Output folder document.
        :type outputFolder: dict
        :param options: Processing options.
        :type options: dict
        """
        self.jobId = jobId
        self.workingSets = workingSets
        self.standardOutput = standardOutput
        self.outputFolder = outputFolder
        self.options = options
