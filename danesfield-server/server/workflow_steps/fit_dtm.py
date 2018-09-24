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

from ..algorithms import fitDtm
from ..constants import DanesfieldStep
from ..workflow_step import DanesfieldWorkflowStep
from ..workflow_utilities import getOptions, getWorkingSet


class FitDtmStep(DanesfieldWorkflowStep):
    """
    Step that runs fit_dtm.

    Supports the following options:
    - iterations
    - tension
    """
    def __init__(self):
        super(FitDtmStep, self).__init__(DanesfieldStep.FIT_DTM)
        self.addDependency(DanesfieldStep.GENERATE_DSM)

    def run(self, jobInfo):
        # Get working sets
        initWorkingSet = getWorkingSet(DanesfieldStep.INIT, jobInfo)
        dsmWorkingSet = getWorkingSet(DanesfieldStep.GENERATE_DSM, jobInfo)

        # Get DSM
        dsmFile = self.getSingleFile(dsmWorkingSet)

        # Get options
        fitDtmOptions = getOptions(self.name, jobInfo)

        # Set output prefix; replacing whitespace with underscores
        outputPrefix = re.sub("\\s", "_", initWorkingSet['name'])

        # Run algorithm
        fitDtm(
            initWorkingSetName=initWorkingSet['name'],
            stepName=self.name, requestInfo=jobInfo.requestInfo, jobId=jobInfo.jobId,
            outputFolder=jobInfo.outputFolder, dsmFile=dsmFile,
            outputPrefix=outputPrefix, **fitDtmOptions)
