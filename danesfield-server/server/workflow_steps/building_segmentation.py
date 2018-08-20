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

import os

from girder.models.item import Item
from girder.models.folder import Folder

from ..algorithms import buildingSegmentation
from ..constants import DanesfieldStep
from ..settings import PluginSettings
from ..workflow import DanesfieldWorkflowException
from ..workflow_step import DanesfieldWorkflowStep
from ..workflow_utilities import fileFromItem, getOptions, getWorkingSet


class BuildingSegmentationStep(DanesfieldWorkflowStep):
    """
    Step that runs building segmentation.

    Supports the following options:
    - <none>
    """
    def __init__(self):
        super(BuildingSegmentationStep, self).__init__(DanesfieldStep.BUILDING_SEGMENTATION)
        self.addDependency(DanesfieldStep.GENERATE_DSM)
        self.addDependency(DanesfieldStep.FIT_DTM)
        self.addDependency(DanesfieldStep.PANSHARPEN)
        self.addDependency(DanesfieldStep.MSI_TO_RGB)

    def run(self, jobInfo):
        # Get working sets
        dsmWorkingSet = getWorkingSet(DanesfieldStep.GENERATE_DSM, jobInfo)
        dtmWorkingSet = getWorkingSet(DanesfieldStep.FIT_DTM, jobInfo)
        pansharpenWorkingSet = getWorkingSet(DanesfieldStep.PANSHARPEN, jobInfo)
        rgbWorkingSet = getWorkingSet(DanesfieldStep.MSI_TO_RGB, jobInfo)

        # Get DSM
        dsmFile = self.getSingleFile(dsmWorkingSet)

        # Get DTM
        dtmFile = self.getSingleFile(dtmWorkingSet)

        # Get the ID of the first pansharpened MSI image
        # TODO: Choose most nadir image
        items = [Item().load(itemId, force=True, exc=True)
                 for itemId in pansharpenWorkingSet['datasetIds']]
        if not items:
            raise DanesfieldWorkflowException('Unable to find pansharpened images', step=self.name)
        msiImageFile = fileFromItem(items[0])

        # Get the ID of the first RGB image
        # TODO: Choose most nadir image
        items = [Item().load(itemId, force=True, exc=True)
                 for itemId in rgbWorkingSet['datasetIds']]
        if not items:
            raise DanesfieldWorkflowException('Unable to find RGB images', step=self.name)
        rgbImageFile = fileFromItem(items[0])

        # Get options
        buildingSegmentationOptions = getOptions(self.name, jobInfo)

        # Get model folder ID from setting
        modelFolder = self.getFolderFromSetting(
            PluginSettings.BUILDING_SEGMENTATION_MODEL_FOLDER_ID)

        # Get model file prefix
        modelFiles = list(Folder().childItems(modelFolder, limit=1))
        if not modelFiles:
            raise DanesfieldWorkflowException(
                'Building segmentation model files not found.', step=self.name)
        modelFilePrefix = os.path.splitext(modelFiles[0]['name'])[0]

        # Run algorithm
        buildingSegmentation(
            stepName=self.name, requestInfo=jobInfo.requestInfo, jobId=jobInfo.jobId,
            outputFolder=jobInfo.outputFolder, dsmFile=dsmFile, dtmFile=dtmFile,
            msiImageFile=msiImageFile, rgbImageFile=rgbImageFile, modelFolder=modelFolder,
            modelFilePrefix=modelFilePrefix, **buildingSegmentationOptions)
