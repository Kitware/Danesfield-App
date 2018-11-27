#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
###############################################################################

import os

from girder.models.folder import Folder

from .select_best import SelectBestStep
from ..algorithms import buildingSegmentation
from ..constants import DanesfieldStep
from ..settings import PluginSettings
from ..utilities import getPrefix
from ..workflow import DanesfieldWorkflowException
from ..workflow_step import DanesfieldWorkflowStep
from ..workflow_utilities import getOptions, getStandardOutput, getWorkingSet


class BuildingSegmentationStep(DanesfieldWorkflowStep):
    """
    Step that runs building segmentation.

    Supports the following options:
    - <none>
    """
    def __init__(self):
        super(BuildingSegmentationStep, self).__init__(
            DanesfieldStep.BUILDING_SEGMENTATION)
        self.addDependency(DanesfieldStep.GENERATE_DSM)
        self.addDependency(DanesfieldStep.FIT_DTM)
        self.addDependency(DanesfieldStep.PANSHARPEN)
        self.addDependency(DanesfieldStep.MSI_TO_RGB)
        self.addDependency(DanesfieldStep.SELECT_BEST)

    def run(self, jobInfo, outputFolder):
        # Get working sets
        initWorkingSet = getWorkingSet(DanesfieldStep.INIT, jobInfo)
        dsmWorkingSet = getWorkingSet(DanesfieldStep.GENERATE_DSM, jobInfo)
        dtmWorkingSet = getWorkingSet(DanesfieldStep.FIT_DTM, jobInfo)
        pansharpenWorkingSet = getWorkingSet(DanesfieldStep.PANSHARPEN,
                                             jobInfo)
        rgbWorkingSet = getWorkingSet(DanesfieldStep.MSI_TO_RGB, jobInfo)

        # Get prefix of best image set
        selectBestStandardOutput = getStandardOutput(
            DanesfieldStep.SELECT_BEST,
            jobInfo)
        prefix = next(
            SelectBestStep.getImagePrefixes(selectBestStandardOutput),
            None)
        if prefix is None:
            raise DanesfieldWorkflowException(
                'Error looking up best image set',
                step=self.name)

        # Get DSM
        dsmFile = self.getSingleFile(dsmWorkingSet)

        # Get DTM
        dtmFile = self.getSingleFile(dtmWorkingSet)

        def hasPrefix(item):
            return getPrefix(item['name']) == prefix

        # Get the best pansharpened MSI image
        msiImageFiles = self.getFiles(pansharpenWorkingSet, hasPrefix)
        if not msiImageFiles:
            raise DanesfieldWorkflowException(
                'Unable to find best pansharpened image', step=self.name)
        msiImageFile = msiImageFiles[0]

        # Get the best RGB image
        rgbImageFiles = self.getFiles(rgbWorkingSet, hasPrefix)
        if not rgbImageFiles:
            raise DanesfieldWorkflowException(
                'Unable to find best RGB image', step=self.name)
        rgbImageFile = rgbImageFiles[0]

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
            initWorkingSetName=initWorkingSet['name'],
            stepName=self.name,
            requestInfo=jobInfo.requestInfo,
            jobId=jobInfo.jobId,
            outputFolder=outputFolder,
            dsmFile=dsmFile,
            dtmFile=dtmFile,
            msiImageFile=msiImageFile,
            rgbImageFile=rgbImageFile,
            modelFolder=modelFolder,
            modelFilePrefix=modelFilePrefix,
            **buildingSegmentationOptions)
