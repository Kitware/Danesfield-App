#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
###############################################################################


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
