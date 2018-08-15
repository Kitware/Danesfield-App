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

from ..algorithms import generateDsm
from ..constants import DanesfieldStep
from ..workflow import DanesfieldWorkflowException, DanesfieldWorkflowStep
from ..workflow_utilities import fileFromItem, getOptions, getWorkingSet, isPointCloud


class GenerateDsmStep(DanesfieldWorkflowStep):
    """
    Step that runs generate_dsm.

    Supports the following options:
    - <none>
    """

    name = DanesfieldStep.GENERATE_DSM

    def __init__(self):
        super(GenerateDsmStep, self).__init__()
        self.addDependency(DanesfieldStep.GENERATE_POINT_CLOUD)

    def run(self, jobInfo):
        stepName = GenerateDsmStep.name

        # Get working sets
        initWorkingSet = getWorkingSet(DanesfieldStep.INIT, jobInfo)
        pointCloudWorkingSet = getWorkingSet(DanesfieldStep.GENERATE_POINT_CLOUD, jobInfo)

        # Get point cloud file
        pointCloudItems = [
            item
            for item in (
                Item().load(itemId, force=True, exc=True)
                for itemId in pointCloudWorkingSet['datasetIds']
            )
            if isPointCloud(item)
        ]
        if not pointCloudItems:
            raise DanesfieldWorkflowException('Unable to find point cloud', step=stepName)
        if len(pointCloudItems) > 1:
            raise DanesfieldWorkflowException(
                'Expected only one point cloud, got {}'.format(len(pointCloudItems)), step=stepName)
        pointCloudFile = fileFromItem(pointCloudItems[0])

        # Get options
        generateDsmOptions = getOptions(stepName, jobInfo)

        # Run algorithm
        generateDsm(
            stepName=stepName, requestInfo=jobInfo.requestInfo, jobId=jobInfo.jobId,
            outputFolder=jobInfo.outputFolder, file=pointCloudFile,
            outputPrefix=initWorkingSet['name'], **generateDsmOptions)
