#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
###############################################################################

from ..algorithms import msiToRgb
from ..constants import DanesfieldStep
from ..workflow_step import DanesfieldWorkflowStep
from ..workflow_utilities import getOptions, getWorkingSet


class MsiToRgbStep(DanesfieldWorkflowStep):
    """
    Step that runs multispectral image (MSI) to RGB conversion.

    Supports the following options:
    - byte
    - alpha
    - rangePercentile
    """

    def __init__(self):
        super(MsiToRgbStep, self).__init__(DanesfieldStep.MSI_TO_RGB)
        self.addDependency(DanesfieldStep.PANSHARPEN)

    def run(self, jobInfo, outputFolder):
        # Get working set
        initWorkingSet = getWorkingSet(DanesfieldStep.INIT, jobInfo)
        pansharpenWorkingSet = getWorkingSet(DanesfieldStep.PANSHARPEN, jobInfo)

        # Get pansharpened MSI images
        imageFiles = self.getFiles(pansharpenWorkingSet)

        # Get options
        msiToRgbOptions = getOptions(self.name, jobInfo)

        # Run algorithm
        msiToRgb(
            initWorkingSetName=initWorkingSet["name"],
            stepName=self.name,
            requestInfo=jobInfo.requestInfo,
            jobId=jobInfo.jobId,
            outputFolder=outputFolder,
            imageFiles=imageFiles,
            **msiToRgbOptions
        )
