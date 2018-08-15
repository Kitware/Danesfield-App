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

from ..algorithms import fitDtm
from ..constants import DanesfieldStep
from ..workflow import DanesfieldWorkflowException, DanesfieldWorkflowStep
from ..workflow_utilities import fileFromItem, getOptions, getWorkingSet


class FitDtmStep(DanesfieldWorkflowStep):
    """
    Step that runs fit_dtm.

    Supports the following options:
    - iterations
    - tension
    """
    name = DanesfieldStep.FIT_DTM

    def __init__(self):
        super(FitDtmStep, self).__init__()
        self.addDependency(DanesfieldStep.GENERATE_DSM)

    def run(self, jobInfo):
        stepName = FitDtmStep.name

        # Get working sets
        initWorkingSet = getWorkingSet(DanesfieldStep.INIT, jobInfo)
        dsmWorkingSet = getWorkingSet(DanesfieldStep.GENERATE_DSM, jobInfo)

        # Get DSM
        items = [Item().load(itemId, force=True, exc=True)
                 for itemId in dsmWorkingSet['datasetIds']]
        if not items:
            raise DanesfieldWorkflowException('Unable to find DSM', step=stepName)
        if len(items) > 1:
            raise DanesfieldWorkflowException(
                'Expected only one input file, got {}'.format(len(items)), step=stepName)
        file = fileFromItem(items[0])

        # Get options
        fitDtmOptions = getOptions(stepName, jobInfo)

        # Run algorithm
        fitDtm(
            stepName=stepName, requestInfo=jobInfo.requestInfo, jobId=jobInfo.jobId,
            outputFolder=jobInfo.outputFolder, file=file, outputPrefix=initWorkingSet['name'],
            **fitDtmOptions)
