#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
###############################################################################

from ..algorithms import orthorectify
from ..constants import DanesfieldStep
from ..workflow_step import DanesfieldWorkflowStep
from ..workflow_utilities import getOptions, getWorkingSet, isMsiImage


class OrthorectifyStep(DanesfieldWorkflowStep):
    """
    Step that runs orthorectify.

    Supports the following options:
    - occlusionThreshold
    - denoiseRadius
    """

    def __init__(self):
        super(OrthorectifyStep, self).__init__(DanesfieldStep.ORTHORECTIFY)
        self.addDependency(DanesfieldStep.GENERATE_POINT_CLOUD)
        self.addDependency(DanesfieldStep.GENERATE_DSM)
        self.addDependency(DanesfieldStep.FIT_DTM)

    def run(self, jobInfo, outputFolder):
        # Get working sets
        initWorkingSet = getWorkingSet(DanesfieldStep.INIT, jobInfo)
        dsmWorkingSet = getWorkingSet(DanesfieldStep.GENERATE_DSM, jobInfo)
        dtmWorkingSet = getWorkingSet(DanesfieldStep.FIT_DTM, jobInfo)

        # Get only MSI source image files
        imageFiles = self.getFiles(initWorkingSet, isMsiImage)

        # Get DSM
        dsmFile = self.getSingleFile(dsmWorkingSet)

        # Get DTM
        dtmFile = self.getSingleFile(dtmWorkingSet)

        # Get options
        orthorectifyOptions = getOptions(self.name, jobInfo)

        # Run algorithm
        orthorectify(
            initWorkingSetName=initWorkingSet["name"],
            stepName=self.name,
            requestInfo=jobInfo.requestInfo,
            jobId=jobInfo.jobId,
            outputFolder=outputFolder,
            imageFiles=imageFiles,
            dsmFile=dsmFile,
            dtmFile=dtmFile,
            **orthorectifyOptions
        )
