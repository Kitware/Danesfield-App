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

from ..algorithms import textureMapping
from ..constants import DanesfieldStep
from ..workflow_step import DanesfieldWorkflowStep
from ..workflow_utilities import (
    getOptions,
    getWorkingSet,
    isObj,
    isCroppedAndPansharpend)


class TextureMappingStep(DanesfieldWorkflowStep):
    """
    Step that runs texture mapping.

    Supports the following options:
    - <none>
    """
    def __init__(self):
        super(TextureMappingStep, self).__init__(
            DanesfieldStep.TEXTURE_MAPPING)
        self.addDependency(DanesfieldStep.ROOF_GEON_EXTRACTION)
        self.addDependency(DanesfieldStep.CROP_AND_PANSHARPEN)
        self.addDependency(DanesfieldStep.GENERATE_DSM)

    def run(self, jobInfo):
        # Get working sets
        initWorkingSet = getWorkingSet(DanesfieldStep.INIT, jobInfo)
        roofGeonExtractionWorkingSet = getWorkingSet(
            DanesfieldStep.ROOF_GEON_EXTRACTION,
            jobInfo)
        dsmWorkingSet = getWorkingSet(DanesfieldStep.GENERATE_DSM, jobInfo)
        cropAndPansharpenWorkingSet = getWorkingSet(
            DanesfieldStep.CROP_AND_PANSHARPEN,
            jobInfo)

        # Get OBJ files
        objFiles = self.getFiles(roofGeonExtractionWorkingSet, isObj)

        # Get cropped + pansharpened images
        imageFiles = self.getFiles(cropAndPansharpenWorkingSet,
                                   isCroppedAndPansharpend)

        # Get DSM
        dsmFile = self.getSingleFile(dsmWorkingSet)

        # Get options
        textureMappingOptions = getOptions(self.name, jobInfo)

        # Run algorithm
        textureMapping(
            initWorkingSetName=initWorkingSet['name'],
            stepName=self.name,
            requestInfo=jobInfo.requestInfo,
            jobId=jobInfo.jobId,
            outputFolder=jobInfo.outputFolder,
            objFiles=objFiles,
            imageFiles=imageFiles,
            dsmFile=dsmFile,
            **textureMappingOptions)
