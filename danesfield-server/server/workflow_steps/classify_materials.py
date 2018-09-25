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

from ..algorithms import classifyMaterials
from ..constants import DanesfieldStep
from ..settings import PluginSettings
from ..workflow_step import DanesfieldWorkflowStep
from ..workflow_utilities import (
    getOptions, getWorkingSet, isMsiImage, isMsiNitfMetadata)


class ClassifyMaterialsStep(DanesfieldWorkflowStep):
    """
    Step that runs material classification.

    Supports the following options:
    - cuda
    - batchSize
    - model
    """
    def __init__(self):
        super(ClassifyMaterialsStep, self).__init__(DanesfieldStep.CLASSIFY_MATERIALS)
        self.addDependency(DanesfieldStep.ORTHORECTIFY)

    def run(self, jobInfo, outputFolder):
        # Get working sets
        initWorkingSet = getWorkingSet(DanesfieldStep.INIT, jobInfo)
        orthorectifyWorkingSet = getWorkingSet(DanesfieldStep.ORTHORECTIFY, jobInfo)

        # Get MSI images
        imageFiles = self.getFiles(orthorectifyWorkingSet, isMsiImage)

        # Get NITF metadata files
        metadataFiles = self.getFiles(initWorkingSet, isMsiNitfMetadata)

        # Get options
        classifyMaterialsOptions = getOptions(self.name, jobInfo)

        # Use model selected from options; get model file from
        # setting.  Not a particularly elegant solution, but should
        # work.
        model = classifyMaterialsOptions.get('model')
        if model == "D1":
            modelFileID = PluginSettings.MATERIAL_CLASSIFIER_D1_MODEL_FILE_ID
        elif model == "D2":
            modelFileID = PluginSettings.MATERIAL_CLASSIFIER_D2_MODEL_FILE_ID
        elif model == "D3":
            modelFileID = PluginSettings.MATERIAL_CLASSIFIER_D3_MODEL_FILE_ID
        elif model == "D4":
            modelFileID = PluginSettings.MATERIAL_CLASSIFIER_D4_MODEL_FILE_ID
        else:
            modelFileID = PluginSettings.MATERIAL_CLASSIFIER_STANDARD_MODEL_FILE_ID

        modelFile = self.getFileFromSetting(modelFileID)

        # Set outfile prefix; replacing whitespace with underscores
        outfilePrefix = re.sub("\\s", "_", initWorkingSet['name'])

        # Run algorithm
        classifyMaterials(
            initWorkingSetName=initWorkingSet['name'],
            stepName=self.name, requestInfo=jobInfo.requestInfo, jobId=jobInfo.jobId,
            outputFolder=outputFolder, imageFiles=imageFiles, metadataFiles=metadataFiles,
            modelFile=modelFile, outfilePrefix=outfilePrefix, **classifyMaterialsOptions)
