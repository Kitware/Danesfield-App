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

    def run(self, jobInfo):
        # Get working set
        pansharpenWorkingSet = getWorkingSet(DanesfieldStep.PANSHARPEN, jobInfo)

        # Get pansharpened MSI images
        imageFiles = self.getFiles(pansharpenWorkingSet)

        # Get options
        msiToRgbOptions = getOptions(self.name, jobInfo)

        # Run algorithm
        msiToRgb(
            stepName=self.name, requestInfo=jobInfo.requestInfo, jobId=jobInfo.jobId,
            outputFolder=jobInfo.outputFolder, imageFiles=imageFiles, **msiToRgbOptions)
