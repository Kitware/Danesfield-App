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

from ..algorithms import pansharpen
from ..constants import DanesfieldStep
from ..workflow import DanesfieldWorkflowStep
from ..workflow_utilities import fileFromItem, getOptions, getWorkingSet, isMsiImage, isPanImage


class PansharpenStep(DanesfieldWorkflowStep):
    """
    Step that runs pansharpen.

    Supports the following options:
    - <none>
    """
    name = DanesfieldStep.PANSHARPEN

    def __init__(self):
        super(PansharpenStep, self).__init__()
        self.addDependency(DanesfieldStep.ORTHORECTIFY)

    def run(self, jobInfo):
        stepName = PansharpenStep.name

        # Get working set
        workingSet = getWorkingSet(DanesfieldStep.ORTHORECTIFY, jobInfo)

        # Get IDs of MSI and PAN source image files
        imageFiles = [
            fileFromItem(item)
            for item in (
                Item().load(itemId, force=True, exc=True)
                for itemId in workingSet['datasetIds']
            )
            if isMsiImage(item) or isPanImage(item)
        ]

        # Get options
        pansharpenOptions = getOptions(stepName, jobInfo)

        # Run algorithm
        pansharpen(
            stepName=stepName, requestInfo=jobInfo.requestInfo, jobId=jobInfo.jobId,
            outputFolder=jobInfo.outputFolder, imageFiles=imageFiles, **pansharpenOptions)
