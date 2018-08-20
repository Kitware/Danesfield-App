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

from ..algorithms import generateDsm
from ..constants import DanesfieldStep
from ..workflow_step import DanesfieldWorkflowStep
from ..workflow_utilities import getOptions, getWorkingSet, isPointCloud


class GenerateDsmStep(DanesfieldWorkflowStep):
    """
    Step that runs generate_dsm.

    Supports the following options:
    - <none>
    """
    def __init__(self):
        super(GenerateDsmStep, self).__init__(DanesfieldStep.GENERATE_DSM)
        self.addDependency(DanesfieldStep.GENERATE_POINT_CLOUD)

    def run(self, jobInfo):
        # Get working sets
        initWorkingSet = getWorkingSet(DanesfieldStep.INIT, jobInfo)
        pointCloudWorkingSet = getWorkingSet(DanesfieldStep.GENERATE_POINT_CLOUD, jobInfo)

        # Get point cloud file
        pointCloudFile = self.getSingleFile(pointCloudWorkingSet, isPointCloud)

        # Get options
        generateDsmOptions = getOptions(self.name, jobInfo)

        # Run algorithm
        generateDsm(
            stepName=self.name, requestInfo=jobInfo.requestInfo, jobId=jobInfo.jobId,
            outputFolder=jobInfo.outputFolder, pointCloudFile=pointCloudFile,
            outputPrefix=initWorkingSet['name'], **generateDsmOptions)
