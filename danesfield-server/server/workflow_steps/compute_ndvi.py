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

import re

from ..algorithms import computeNdvi
from ..constants import DanesfieldStep
from ..workflow_step import DanesfieldWorkflowStep
from ..workflow_utilities import getOptions, getWorkingSet, isMsiImage


class ComputeNdviStep(DanesfieldWorkflowStep):
    """
    Step that computes the NDVI from the pansharpened images.

    Supports the following options:
    - <none>
    """
    def __init__(self):
        super(ComputeNdviStep, self).__init__(DanesfieldStep.COMPUTE_NDVI)
        self.addDependency(DanesfieldStep.ORTHORECTIFY)

    def run(self, jobInfo, outputFolder):
        # Get working sets
        initWorkingSet = getWorkingSet(DanesfieldStep.INIT, jobInfo)
        orthorectifyWorkingSet = getWorkingSet(
            DanesfieldStep.ORTHORECTIFY,
            jobInfo)

        # Get pansharpened images
        imageFiles = self.getFiles(orthorectifyWorkingSet, isMsiImage)

        # Get options
        computeNdviOptions = getOptions(self.name, jobInfo)

        # Set output filename
        outputPrefix = re.sub("\\s", "_", initWorkingSet['name'])
        outputNdviFilename = "%s_NDVI.tif" % outputPrefix

        # Run algorithm
        computeNdvi(
            initWorkingSetName=initWorkingSet['name'],
            stepName=self.name,
            requestInfo=jobInfo.requestInfo,
            jobId=jobInfo.jobId,
            outputFolder=outputFolder,
            imageFiles=imageFiles,
            outputNdviFilename=outputNdviFilename,
            **computeNdviOptions)
