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

from girder.models.item import Item

from ..algorithms import msiToRgb
from ..constants import DanesfieldStep
from ..workflow import DanesfieldWorkflowStep
from ..workflow_utilities import fileFromItem, getOptions, getWorkingSet


class MsiToRgbStep(DanesfieldWorkflowStep):
    """
    Step that runs multispectral image (MSI) to RGB conversion.

    Supports the following options:
    - byte
    - alpha
    - rangePercentile
    """
    name = DanesfieldStep.MSI_TO_RGB

    def __init__(self):
        super(MsiToRgbStep, self).__init__()
        self.addDependency(DanesfieldStep.PANSHARPEN)

    def run(self, jobInfo):
        stepName = MsiToRgbStep.name

        # Get working set
        workingSet = getWorkingSet(DanesfieldStep.PANSHARPEN, jobInfo)

        # Get IDs of pansharpened MSI images
        imageFiles = [
            fileFromItem(item)
            for item in (
                Item().load(itemId, force=True, exc=True)
                for itemId in workingSet['datasetIds']
            )
        ]

        # Get options
        msiToRgbOptions = getOptions(stepName, jobInfo)

        # Run algorithm
        msiToRgb(
            stepName=stepName, requestInfo=jobInfo.requestInfo, jobId=jobInfo.jobId,
            outputFolder=jobInfo.outputFolder, imageFiles=imageFiles, **msiToRgbOptions)
