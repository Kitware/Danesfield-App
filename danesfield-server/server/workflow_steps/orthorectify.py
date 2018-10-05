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

from ..algorithms import orthorectify
from ..constants import DanesfieldStep
from ..workflow_step import DanesfieldWorkflowStep
from ..workflow_utilities import (
    getOptions, getWorkingSet, isMsiImage, isRpc)


class OrthorectifyStep(DanesfieldWorkflowStep):
    """
    Step that runs orthorectify.

    Supports the following options:
    - occlusionThreshold
    - denoiseRadius
    """
    def __init__(self):
        super(OrthorectifyStep, self).__init__(DanesfieldStep.ORTHORECTIFY)
        self.addDependency(DanesfieldStep.GENERATE_POINT_CLOUD)
        self.addDependency(DanesfieldStep.GENERATE_DSM)
        self.addDependency(DanesfieldStep.FIT_DTM)

    def run(self, jobInfo, outputFolder):
        # Get working sets
        initWorkingSet = getWorkingSet(DanesfieldStep.INIT, jobInfo)
        dsmWorkingSet = getWorkingSet(DanesfieldStep.GENERATE_DSM, jobInfo)
        dtmWorkingSet = getWorkingSet(DanesfieldStep.FIT_DTM, jobInfo)
        pointCloudWorkingSet = getWorkingSet(
            DanesfieldStep.GENERATE_POINT_CLOUD, jobInfo)

        # Get only MSI source image files
        imageFiles = self.getFiles(initWorkingSet, isMsiImage)

        # Get DSM
        dsmFile = self.getSingleFile(dsmWorkingSet)

        # Get DTM
        dtmFile = self.getSingleFile(dtmWorkingSet)

        # Get updated RPC files
        rpcFiles = self.getFiles(pointCloudWorkingSet, isRpc)

        # Get options
        orthorectifyOptions = getOptions(self.name, jobInfo)

        # Run algorithm
        orthorectify(
            initWorkingSetName=initWorkingSet['name'],
            stepName=self.name,
            requestInfo=jobInfo.requestInfo,
            jobId=jobInfo.jobId,
            outputFolder=outputFolder,
            imageFiles=imageFiles,
            dsmFile=dsmFile,
            dtmFile=dtmFile,
            rpcFiles=rpcFiles,
            **orthorectifyOptions)
