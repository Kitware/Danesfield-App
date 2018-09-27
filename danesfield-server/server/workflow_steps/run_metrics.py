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

from ..algorithms import runMetrics
from ..constants import DanesfieldStep
from ..settings import PluginSettings
from ..workflow_step import DanesfieldWorkflowStep
from ..workflow_utilities import (
    getOptions, getWorkingSet, isClsImage, isDsmImage, isMtlImage)


class RunMetricsStep(DanesfieldWorkflowStep):
    """
    Step that runs the pubgeo core3d metrics.
    """

    def __init__(self):
        super(RunMetricsStep, self).__init__(DanesfieldStep.RUN_METRICS)
        self.addDependency(DanesfieldStep.CLASSIFY_MATERIALS)
        self.addDependency(DanesfieldStep.BUILDINGS_TO_DSM)
        self.addDependency(DanesfieldStep.FIT_DTM)

    def run(self, jobInfo):
        # Get working sets
        initWorkingSet = getWorkingSet(DanesfieldStep.INIT, jobInfo)
        classifyMaterialsWorkingSet = getWorkingSet(DanesfieldStep.CLASSIFY_MATERIALS, jobInfo)
        buildingsToDsmWorkingSet = getWorkingSet(DanesfieldStep.BUILDINGS_TO_DSM, jobInfo)
        dtmWorkingSet = getWorkingSet(DanesfieldStep.FIT_DTM, jobInfo)

        runMetricsOptions = getOptions(self.name, jobInfo)
        classifyMaterialsOptions = getOptions(DanesfieldStep.CLASSIFY_MATERIALS, jobInfo)

        # Using the "model" passed through the classify materials
        # options as the reference file prefix for now
        referencePrefix = classifyMaterialsOptions.get('model')

        referenceFolder = self.getFolderFromSetting(
            PluginSettings.REFERENCE_DATA_FOLDER_ID)

        # Get DTM
        dtmFile = self.getSingleFile(dtmWorkingSet)

        # Get CLS
        clsFile = self.getSingleFile(buildingsToDsmWorkingSet, isClsImage)

        # Get DSM
        dsmFile = self.getSingleFile(buildingsToDsmWorkingSet, isDsmImage)

        # Get MTL
        mtlFile = self.getSingleFile(classifyMaterialsWorkingSet, isMtlImage)

        # Run algorithm
        runMetrics(
            initWorkingSetName=initWorkingSet['name'],
            stepName=self.name,
            requestInfo=jobInfo.requestInfo,
            jobId=jobInfo.jobId,
            outputFolder=jobInfo.outputFolder,
            referenceFolder=referenceFolder,
            referencePrefix=referencePrefix,
            dtmFile=dtmFile,
            dsmFile=dsmFile,
            clsFile=clsFile,
            mtlFile=mtlFile,
            **runMetricsOptions)
