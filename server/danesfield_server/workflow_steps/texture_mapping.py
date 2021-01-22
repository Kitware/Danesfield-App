#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
###############################################################################

from ..algorithms import textureMapping
from ..constants import DanesfieldStep
from ..workflow_step import DanesfieldWorkflowStep
from ..workflow_utilities import (
    getOptions,
    getWorkingSet,
    isObj,
    isCroppedAndPansharpend,
)


class TextureMappingStep(DanesfieldWorkflowStep):
    """
    Step that runs texture mapping.

    Supports the following options:
    - <none>
    """

    def __init__(self):
        super(TextureMappingStep, self).__init__(DanesfieldStep.TEXTURE_MAPPING)
        self.addDependency(DanesfieldStep.ROOF_GEON_EXTRACTION)
        self.addDependency(DanesfieldStep.CROP_AND_PANSHARPEN)
        self.addDependency(DanesfieldStep.GENERATE_DSM)
        self.addDependency(DanesfieldStep.FIT_DTM)

    def run(self, jobInfo, outputFolder):
        # Get working sets
        initWorkingSet = getWorkingSet(DanesfieldStep.INIT, jobInfo)
        roofGeonExtractionWorkingSet = getWorkingSet(
            DanesfieldStep.ROOF_GEON_EXTRACTION, jobInfo
        )
        dsmWorkingSet = getWorkingSet(DanesfieldStep.GENERATE_DSM, jobInfo)
        cropAndPansharpenWorkingSet = getWorkingSet(
            DanesfieldStep.CROP_AND_PANSHARPEN, jobInfo
        )
        dtmWorkingSet = getWorkingSet(DanesfieldStep.FIT_DTM, jobInfo)

        # Get OBJ files
        objFiles = self.getFiles(roofGeonExtractionWorkingSet, isObj)

        # Get cropped + pansharpened images
        imageFiles = self.getFiles(cropAndPansharpenWorkingSet, isCroppedAndPansharpend)

        # Get DSM
        dsmFile = self.getSingleFile(dsmWorkingSet)

        # Get DTM
        dtmFile = self.getSingleFile(dtmWorkingSet)

        # Get options
        textureMappingOptions = getOptions(self.name, jobInfo)

        # Run algorithm
        textureMapping(
            initWorkingSetName=initWorkingSet["name"],
            stepName=self.name,
            requestInfo=jobInfo.requestInfo,
            jobId=jobInfo.jobId,
            outputFolder=outputFolder,
            objFiles=objFiles,
            imageFiles=imageFiles,
            dsmFile=dsmFile,
            dtmFile=dtmFile,
            **textureMappingOptions
        )
