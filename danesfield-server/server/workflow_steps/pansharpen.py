#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
###############################################################################



from ..algorithms import pansharpen
from ..constants import DanesfieldStep
from ..workflow_step import DanesfieldWorkflowStep
from ..workflow_utilities import getOptions, getWorkingSet, isMsiImage, isPanImage


class PansharpenStep(DanesfieldWorkflowStep):
    """
    Step that runs pansharpen.

    Supports the following options:
    - <none>
    """
    def __init__(self):
        super(PansharpenStep, self).__init__(DanesfieldStep.PANSHARPEN)
        self.addDependency(DanesfieldStep.ORTHORECTIFY)

    def run(self, jobInfo, outputFolder):
        # Get working set
        initWorkingSet = getWorkingSet(DanesfieldStep.INIT, jobInfo)
        orthorectifyWorkingSet = getWorkingSet(DanesfieldStep.ORTHORECTIFY, jobInfo)

        # Get MSI and PAN source image files
        imageFiles = self.getFiles(
            orthorectifyWorkingSet,
            lambda item: isMsiImage(item) or isPanImage(item))

        # Get options
        pansharpenOptions = getOptions(self.name, jobInfo)

        # Run algorithm
        pansharpen(
            initWorkingSetName=initWorkingSet['name'],
            stepName=self.name, requestInfo=jobInfo.requestInfo, jobId=jobInfo.jobId,
            outputFolder=outputFolder, imageFiles=imageFiles, **pansharpenOptions)
