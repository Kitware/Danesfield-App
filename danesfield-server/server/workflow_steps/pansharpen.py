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

    def run(self, jobInfo):
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
            outputFolder=jobInfo.outputFolder, imageFiles=imageFiles, **pansharpenOptions)
