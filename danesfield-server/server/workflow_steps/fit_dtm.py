#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
###############################################################################

import re

from ..algorithms import fitDtm
from ..constants import DanesfieldStep
from ..workflow_step import DanesfieldWorkflowStep
from ..workflow_utilities import getOptions, getWorkingSet


class FitDtmStep(DanesfieldWorkflowStep):
    """
    Step that runs fit_dtm.

    Supports the following options:
    - iterations
    - tension
    """
    def __init__(self):
        super(FitDtmStep, self).__init__(DanesfieldStep.FIT_DTM)
        self.addDependency(DanesfieldStep.GENERATE_DSM)

    def run(self, jobInfo, outputFolder):
        # Get working sets
        initWorkingSet = getWorkingSet(DanesfieldStep.INIT, jobInfo)
        dsmWorkingSet = getWorkingSet(DanesfieldStep.GENERATE_DSM, jobInfo)

        # Get DSM
        dsmFile = self.getSingleFile(dsmWorkingSet)

        # Get options
        fitDtmOptions = getOptions(self.name, jobInfo)

        # Set output prefix; replacing whitespace with underscores
        outputPrefix = re.sub("\\s", "_", initWorkingSet['name'])

        # Run algorithm
        fitDtm(
            initWorkingSetName=initWorkingSet['name'],
            stepName=self.name,
            requestInfo=jobInfo.requestInfo,
            jobId=jobInfo.jobId,
            outputFolder=outputFolder,
            dsmFile=dsmFile,
            outputPrefix=outputPrefix,
            **fitDtmOptions)
