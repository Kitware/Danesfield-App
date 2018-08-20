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

import os

from ..algorithms import selectBest
from ..constants import DanesfieldStep
from ..utilities import getPrefix
from ..workflow_step import DanesfieldWorkflowStep
from ..workflow_utilities import getOptions, getWorkingSet, isPanImage


class SelectBestStep(DanesfieldWorkflowStep):
    """
    Step that runs select_best.

    Supports the following options:
    - <none>
    """
    def __init__(self):
        super(SelectBestStep, self).__init__(DanesfieldStep.SELECT_BEST)
        self.addDependency(DanesfieldStep.GENERATE_DSM)

    def run(self, jobInfo):
        # Get working sets
        initWorkingSet = getWorkingSet(DanesfieldStep.INIT, jobInfo)
        dsmWorkingSet = getWorkingSet(DanesfieldStep.GENERATE_DSM, jobInfo)

        # TODO: check PAN vs MSI
        # Get PAN source image files
        imageFiles = self.getFiles(initWorkingSet, isPanImage)

        # Get DSM
        dsmFile = self.getSingleFile(dsmWorkingSet)

        # Get options
        selectBestOptions = getOptions(self.name, jobInfo)

        # Run algorithm
        selectBest(
            stepName=self.name, requestInfo=jobInfo.requestInfo, jobId=jobInfo.jobId,
            outputFolder=jobInfo.outputFolder, imageFiles=imageFiles, dsmFile=dsmFile,
            **selectBestOptions)

    @staticmethod
    def getImagePrefixes(output):
        """
        Parse output from select_best and return generator of image prefixes.
        Output argument is a list of strings, where each string may contain
        multiple lines.
        """
        prefix = None
        for group in output:
            lines = group.splitlines()
            for line in lines:
                filename = os.path.basename(line)
                prefix = getPrefix(filename)
                if prefix is not None:
                    yield prefix
