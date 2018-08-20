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

from girder.models.file import File
from girder.models.item import Item
from girder.models.setting import Setting

from ..algorithms import classifyMaterials
from ..constants import DanesfieldStep
from ..settings import PluginSettings
from ..workflow import DanesfieldWorkflowException, DanesfieldWorkflowStep
from ..workflow_utilities import (
    fileFromItem, getOptions, getWorkingSet, isMsiImage, isMsiNitfMetadata)


class ClassifyMaterialsStep(DanesfieldWorkflowStep):
    """
    Step that runs material classification.

    Supports the following options:
    - cuda
    - batchSize
    """
    name = DanesfieldStep.CLASSIFY_MATERIALS

    def __init__(self):
        super(ClassifyMaterialsStep, self).__init__()
        self.addDependency(DanesfieldStep.ORTHORECTIFY)

    def run(self, jobInfo):
        stepName = ClassifyMaterialsStep.name

        # Get working sets
        initWorkingSet = getWorkingSet(DanesfieldStep.INIT, jobInfo)
        orthorectifyWorkingSet = getWorkingSet(DanesfieldStep.ORTHORECTIFY, jobInfo)

        # Get IDs of MSI images
        imageFiles = [
            fileFromItem(item)
            for item in (
                Item().load(itemId, force=True, exc=True)
                for itemId in orthorectifyWorkingSet['datasetIds']
            )
            if isMsiImage(item)
        ]

        # Get IDs of NITF metadata files
        metadataFiles = [
            fileFromItem(item)
            for item in (
                Item().load(itemId, force=True, exc=True)
                for itemId in initWorkingSet['datasetIds']
            )
            if isMsiNitfMetadata(item)
        ]

        # Get options
        classifyMaterialsOptions = getOptions(stepName, jobInfo)

        # Get model file from setting
        modelFileId = Setting().get(PluginSettings.MATERIAL_CLASSIFIER_MODEL_FILE_ID)
        if not modelFileId:
            raise DanesfieldWorkflowException(
                'Invalid material classifier model file ID: {}'.format(modelFileId), step=stepName)
        modelFile = File().load(modelFileId, force=True, exc=True)
        if not modelFile:
            raise DanesfieldWorkflowException(
                'Material classifier model file not found', step=stepName)

        # Run algorithm
        classifyMaterials(
            stepName=stepName, requestInfo=jobInfo.requestInfo, jobId=jobInfo.jobId,
            outputFolder=jobInfo.outputFolder, imageFiles=imageFiles, metadataFiles=metadataFiles,
            modelFile=modelFile, **classifyMaterialsOptions)
