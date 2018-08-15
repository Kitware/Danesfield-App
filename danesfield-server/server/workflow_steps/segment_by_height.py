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

from ..algorithms import segmentByHeight
from ..constants import DanesfieldStep
from ..workflow import DanesfieldWorkflowException, DanesfieldWorkflowStep
from ..workflow_utilities import fileFromItem, getOptions, getWorkingSet


class SegmentByHeightStep(DanesfieldWorkflowStep):
    """
    Step that runs segment by height.

    Supports the following options:
    - <none>
    """
    name = DanesfieldStep.SEGMENT_BY_HEIGHT

    def __init__(self):
        super(SegmentByHeightStep, self).__init__()
        self.addDependency(DanesfieldStep.GENERATE_DSM)
        self.addDependency(DanesfieldStep.FIT_DTM)
        self.addDependency(DanesfieldStep.PANSHARPEN)

    def run(self, jobInfo):
        stepName = SegmentByHeightStep.name

        # Get working sets
        dsmWorkingSet = getWorkingSet(DanesfieldStep.GENERATE_DSM, jobInfo)
        dtmWorkingSet = getWorkingSet(DanesfieldStep.FIT_DTM, jobInfo)
        pansharpenWorkingSet = getWorkingSet(DanesfieldStep.PANSHARPEN, jobInfo)

        # Get DSM
        items = [Item().load(itemId, force=True, exc=True)
                 for itemId in dsmWorkingSet['datasetIds']]
        if not items:
            raise DanesfieldWorkflowException('Unable to find DSM', step=stepName)
        if len(items) > 1:
            raise DanesfieldWorkflowException(
                'Expected only one input file, got {}'.format(len(items)), step=stepName)
        dsmFile = fileFromItem(items[0])

        # Get DTM
        items = [Item().load(itemId, force=True, exc=True)
                 for itemId in dtmWorkingSet['datasetIds']]
        if not items:
            raise DanesfieldWorkflowException('Unable to find DTM', step=stepName)
        if len(items) > 1:
            raise DanesfieldWorkflowException(
                'Expected only one input file, got {}'.format(len(items)), step=stepName)
        dtmFile = fileFromItem(items[0])

        # Get the ID of the first pansharpened MSI image
        # TODO: Choose most nadir image, likely determined by a previous step
        # and a new tool based on metadata in the source PAN images
        items = [Item().load(itemId, force=True, exc=True)
                 for itemId in pansharpenWorkingSet['datasetIds']]
        if not items:
            raise DanesfieldWorkflowException('Unable to find pansharpened images', step=stepName)
        msiImageFile = fileFromItem(items[0])

        # Get options
        segmentByHeightOptions = getOptions(stepName, jobInfo)

        # Run algorithm
        segmentByHeight(
            stepName=stepName, requestInfo=jobInfo.requestInfo, jobId=jobInfo.jobId,
            outputFolder=jobInfo.outputFolder, dsmFile=dsmFile, dtmFile=dtmFile,
            msiImageFile=msiImageFile, **segmentByHeightOptions)
