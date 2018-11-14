#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
###############################################################################



from ..algorithms import cropAndPansharpen
from ..constants import DanesfieldStep
from ..workflow_step import DanesfieldWorkflowStep
from ..workflow_utilities import (
    getOptions,
    getWorkingSet,
    isMsiImage,
    isPanImage,
    isMsiRpc,
    isPanRpc)


class CropAndPansharpenStep(DanesfieldWorkflowStep):
    """
    Step that runs cropping and pansharpening for texture mapping
    generation
    """
    def __init__(self):
        super(CropAndPansharpenStep, self).__init__(
            DanesfieldStep.CROP_AND_PANSHARPEN)
        self.addDependency(DanesfieldStep.GENERATE_POINT_CLOUD)
        self.addDependency(DanesfieldStep.GENERATE_DSM)

    def run(self, jobInfo, outputFolder):
        # Get working sets
        initWorkingSet = getWorkingSet(DanesfieldStep.INIT, jobInfo)
        pointCloudWorkingSet = getWorkingSet(
            DanesfieldStep.GENERATE_POINT_CLOUD,
            jobInfo)
        dsmWorkingSet = getWorkingSet(DanesfieldStep.GENERATE_DSM, jobInfo)

        # Get DSM
        dsmFile = self.getSingleFile(dsmWorkingSet)

        # Get MSI source image files
        msiImageFiles = self.getFiles(
            initWorkingSet,
            isMsiImage)

        # Get PAN source image files
        panImageFiles = self.getFiles(
            initWorkingSet,
            isPanImage)

        # Get updated MSI RPC files
        msiRpcFiles = self.getFiles(pointCloudWorkingSet, isMsiRpc)

        # Get updated PAN RPC files
        panRpcFiles = self.getFiles(pointCloudWorkingSet, isPanRpc)

        # Get options
        cropAndPansharpenOptions = getOptions(self.name, jobInfo)

        # Run algorithm
        cropAndPansharpen(
            initWorkingSetName=initWorkingSet['name'],
            stepName=self.name,
            requestInfo=jobInfo.requestInfo,
            jobId=jobInfo.jobId,
            outputFolder=outputFolder,
            dsmFile=dsmFile,
            msiImageFiles=msiImageFiles,
            panImageFiles=panImageFiles,
            msiRpcFiles=msiRpcFiles,
            panRpcFiles=panRpcFiles,
            **cropAndPansharpenOptions)
