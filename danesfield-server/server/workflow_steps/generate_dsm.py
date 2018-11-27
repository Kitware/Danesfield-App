#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
###############################################################################

import re

from ..algorithms import generateDsm
from ..constants import DanesfieldStep
from ..workflow_step import DanesfieldWorkflowStep
from ..workflow_utilities import getOptions, getWorkingSet, isPointCloud


class GenerateDsmStep(DanesfieldWorkflowStep):
    """
    Step that runs generate_dsm.

    Supports the following options:
    - <none>
    """
    def __init__(self):
        super(GenerateDsmStep, self).__init__(DanesfieldStep.GENERATE_DSM)
        self.addDependency(DanesfieldStep.GENERATE_POINT_CLOUD)

    def run(self, jobInfo, outputFolder):
        # Get working sets
        initWorkingSet = getWorkingSet(DanesfieldStep.INIT, jobInfo)
        pointCloudWorkingSet = getWorkingSet(
            DanesfieldStep.GENERATE_POINT_CLOUD,
            jobInfo)

        # Get point cloud file
        pointCloudFile = self.getSingleFile(pointCloudWorkingSet, isPointCloud)

        # Get options
        generateDsmOptions = getOptions(self.name, jobInfo)

        # Set output prefix; replacing whitespace with underscores
        outputPrefix = re.sub("\\s", "_", initWorkingSet['name'])

        # Run algorithm
        generateDsm(
            initWorkingSetName=initWorkingSet['name'],
            stepName=self.name,
            requestInfo=jobInfo.requestInfo,
            jobId=jobInfo.jobId,
            outputFolder=outputFolder,
            pointCloudFile=pointCloudFile,
            outputPrefix=outputPrefix,
            **generateDsmOptions)
