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

from ..algorithms import unetSemanticSegmentation
from ..constants import DanesfieldStep
from ..settings import PluginSettings
from ..workflow import DanesfieldWorkflowException, DanesfieldWorkflowStep
from ..workflow_utilities import fileFromItem, getOptions, getWorkingSet


class UNetSemanticSegmentationStep(DanesfieldWorkflowStep):
    """
    Step that runs UNet semantic segmentation.

    Supports the following options:
    - <none>
    """
    name = DanesfieldStep.UNET_SEMANTIC_SEGMENTATION

    def __init__(self):
        super(UNetSemanticSegmentationStep, self).__init__()
        self.addDependency(DanesfieldStep.GENERATE_DSM)
        self.addDependency(DanesfieldStep.FIT_DTM)
        self.addDependency(DanesfieldStep.PANSHARPEN)
        self.addDependency(DanesfieldStep.MSI_TO_RGB)

    def run(self, jobInfo):
        stepName = UNetSemanticSegmentationStep.name

        # Get working sets
        dsmWorkingSet = getWorkingSet(DanesfieldStep.GENERATE_DSM, jobInfo)
        dtmWorkingSet = getWorkingSet(DanesfieldStep.FIT_DTM, jobInfo)
        pansharpenWorkingSet = getWorkingSet(DanesfieldStep.PANSHARPEN, jobInfo)
        rgbWorkingSet = getWorkingSet(DanesfieldStep.MSI_TO_RGB, jobInfo)

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
        # TODO: Choose most nadir image
        items = [Item().load(itemId, force=True, exc=True)
                 for itemId in pansharpenWorkingSet['datasetIds']]
        if not items:
            raise DanesfieldWorkflowException('Unable to find pansharpened images', step=stepName)
        msiImageFile = fileFromItem(items[0])

        # Get the ID of the first RGB image
        # TODO: Choose most nadir image
        items = [Item().load(itemId, force=True, exc=True)
                 for itemId in rgbWorkingSet['datasetIds']]
        if not items:
            raise DanesfieldWorkflowException('Unable to find RGB images', step=stepName)
        rgbImageFile = fileFromItem(items[0])

        # Get options
        unetSemanticSegmentationOptions = getOptions(stepName, jobInfo)

        # Get configuration file from setting
        configFileId = Setting().get(PluginSettings.UNET_SEMANTIC_SEGMENTATION_CONFIG_FILE_ID)
        if not configFileId:
            raise DanesfieldWorkflowException(
                'Invalid UNet semantic segmentation config file ID: {}'.format(configFileId),
                step=stepName)
        configFile = File().load(configFileId, force=True, exc=True)
        if not configFile:
            raise DanesfieldWorkflowException(
                'UNet semantic segmentation config file not found', step=stepName)

        # Get model file from setting
        modelFileId = Setting().get(PluginSettings.UNET_SEMANTIC_SEGMENTATION_MODEL_FILE_ID)
        if not modelFileId:
            raise DanesfieldWorkflowException(
                'Invalid UNet semantic segmentation model file ID: {}'.format(modelFileId),
                step=stepName)
        modelFile = File().load(modelFileId, force=True, exc=True)
        if not modelFile:
            raise DanesfieldWorkflowException(
                'UNet semantic segmentation model file not found', step=stepName)

        # Run algorithm
        unetSemanticSegmentation(
            stepName=stepName, requestInfo=jobInfo.requestInfo, jobId=jobInfo.jobId,
            outputFolder=jobInfo.outputFolder, dsmFile=dsmFile, dtmFile=dtmFile,
            msiImageFile=msiImageFile, rgbImageFile=rgbImageFile, configFile=configFile,
            modelFile=modelFile, **unetSemanticSegmentationOptions)
