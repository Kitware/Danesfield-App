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

from ..algorithms import orthorectify
from ..constants import DanesfieldStep
from ..workflow import DanesfieldWorkflowException, DanesfieldWorkflowStep
from ..workflow_utilities import (
    fileFromItem, getOptions, getWorkingSet, isMsiImage, isPanImage, isRpc)


class OrthorectifyStep(DanesfieldWorkflowStep):
    """
    Step that runs orthorectify.

    Supports the following options:
    - occlusionThreshold
    - denoiseRadius
    """
    name = DanesfieldStep.ORTHORECTIFY

    def __init__(self):
        super(OrthorectifyStep, self).__init__()
        self.addDependency(DanesfieldStep.GENERATE_POINT_CLOUD)
        self.addDependency(DanesfieldStep.GENERATE_DSM)
        self.addDependency(DanesfieldStep.FIT_DTM)

    def run(self, jobInfo):
        stepName = OrthorectifyStep.name

        # Get working sets
        initWorkingSet = getWorkingSet(DanesfieldStep.INIT, jobInfo)
        dsmWorkingSet = getWorkingSet(DanesfieldStep.GENERATE_DSM, jobInfo)
        dtmWorkingSet = getWorkingSet(DanesfieldStep.FIT_DTM, jobInfo)
        pointCloudWorkingSet = getWorkingSet(DanesfieldStep.GENERATE_POINT_CLOUD, jobInfo)

        # Get IDs of MSI and PAN source image files
        imageFiles = [
            fileFromItem(item)
            for item in (
                Item().load(itemId, force=True, exc=True)
                for itemId in initWorkingSet['datasetIds']
            )
            if isMsiImage(item) or isPanImage(item)
        ]

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

        # Get updated RPC files
        rpcFiles = [
            fileFromItem(item)
            for item in (
                Item().load(itemId, force=True, exc=True)
                for itemId in pointCloudWorkingSet['datasetIds']
            )
            if isRpc(item)
        ]

        # Get options
        orthorectifyOptions = getOptions(stepName, jobInfo)

        # Run algorithm
        orthorectify(
            stepName=stepName, requestInfo=jobInfo.requestInfo, jobId=jobInfo.jobId,
            outputFolder=jobInfo.outputFolder, imageFiles=imageFiles, dsmFile=dsmFile,
            dtmFile=dtmFile, rpcFiles=rpcFiles, **orthorectifyOptions)
