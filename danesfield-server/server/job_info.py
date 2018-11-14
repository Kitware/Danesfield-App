#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
###############################################################################




class JobInfo:
    """
    Class to store Danesfield job information.
    A job is an instance of a running workflow.
    """
    def __init__(self, jobId, requestInfo, workingSets, standardOutput, outputFolder, options):
        """
        :param jobId: Identifier of Danesfield job.
        :type jobId: str
        :param requestInfo: HTTP request and authorization info.
        :type requestInfo: RequestInfo
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
        self.requestInfo = requestInfo
        self.workingSets = workingSets
        self.standardOutput = standardOutput
        self.outputFolder = outputFolder
        self.options = options
