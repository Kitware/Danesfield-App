#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
###############################################################################

import os

from girder.models.folder import Folder

from ..algorithms import roofGeonExtraction
from ..constants import DanesfieldStep
from ..settings import PluginSettings
from ..workflow import DanesfieldWorkflowException
from ..workflow_step import DanesfieldWorkflowStep
from ..workflow_utilities import (
    getOptions,
    getWorkingSet,
    isClsImage,
    isPointCloud)


class RoofGeonExtractionStep(DanesfieldWorkflowStep):
    """
    Step that runs Purdue and Columbia's roof geon extraction.

    Supports the following options:
    - <none>
    """
    def __init__(self):
        super(RoofGeonExtractionStep, self).__init__(
            DanesfieldStep.ROOF_GEON_EXTRACTION)
        self.addDependency(DanesfieldStep.GENERATE_POINT_CLOUD)
        self.addDependency(DanesfieldStep.FIT_DTM)
        # TODO: Choose one of:
        self.addDependency(DanesfieldStep.SEGMENT_BY_HEIGHT)
        # self.addDependency(DanesfieldStep.BUILDING_SEGMENTATION)
        # self.addDependency(DanesfieldStep.UNET_SEMANTIC_SEGMENTATION)

    def run(self, jobInfo, outputFolder):
        # Get working sets
        initWorkingSet = getWorkingSet(DanesfieldStep.INIT, jobInfo)
        pointCloudWorkingSet = getWorkingSet(
            DanesfieldStep.GENERATE_POINT_CLOUD,
            jobInfo)
        dtmWorkingSet = getWorkingSet(DanesfieldStep.FIT_DTM, jobInfo)
        buildingSegmentationWorkingSet = getWorkingSet(
            DanesfieldStep.SEGMENT_BY_HEIGHT, jobInfo)

        # Get point cloud file
        pointCloudFile = self.getSingleFile(pointCloudWorkingSet, isPointCloud)

        # Get DTM
        dtmFile = self.getSingleFile(dtmWorkingSet)

        # Get building mask
        buildingMaskFiles = self.getFiles(
            buildingSegmentationWorkingSet,
            isClsImage)
        if not buildingMaskFiles:
            raise DanesfieldWorkflowException(
                'Unable to find building mask',
                step=self.name)
        buildingMaskFile = buildingMaskFiles[0]

        # Get options
        roofGeonExtractionOptions = getOptions(self.name, jobInfo)

# Get model folder ID from setting
        modelFolder = self.getFolderFromSetting(
            PluginSettings.ROOF_SEGMENTATION_MODEL_FOLDER_ID)

        # Get model file prefix
        modelFiles = list(Folder().childItems(modelFolder, limit=1))
        if not modelFiles:
            raise DanesfieldWorkflowException(
                'Roof segmentation model files not found.', step=self.name)
        modelFilePrefix = os.path.splitext(modelFiles[0]['name'])[0]

        # Run algorithm
        roofGeonExtraction(
            initWorkingSetName=initWorkingSet['name'],
            stepName=self.name,
            requestInfo=jobInfo.requestInfo,
            jobId=jobInfo.jobId,
            outputFolder=outputFolder,
            pointCloudFile=pointCloudFile,
            dtmFile=dtmFile,
            buildingMaskFile=buildingMaskFile,
            modelFolder=modelFolder,
            modelFilePrefix=modelFilePrefix,
            **roofGeonExtractionOptions)
