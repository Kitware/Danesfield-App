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

from ..algorithms import roofGeonExtraction
from ..constants import DanesfieldStep
from ..workflow import DanesfieldWorkflowException
from ..workflow_step import DanesfieldWorkflowStep
from ..workflow_utilities import getOptions, getWorkingSet, isClsImage, isPointCloud


class RoofGeonExtractionStep(DanesfieldWorkflowStep):
    """
    Step that runs Purdue roof geon extraction.

    Supports the following options:
    - <none>
    """
    def __init__(self):
        super(RoofGeonExtractionStep, self).__init__(DanesfieldStep.ROOF_GEON_EXTRACTION)
        self.addDependency(DanesfieldStep.GENERATE_POINT_CLOUD)
        self.addDependency(DanesfieldStep.FIT_DTM)
        # TODO: Choose one of:
        # self.addDependency(DanesfieldStep.SEGMENT_BY_HEIGHT)
        # self.addDependency(DanesfieldStep.BUILDING_SEGMENTATION)
        self.addDependency(DanesfieldStep.UNET_SEMANTIC_SEGMENTATION)

    def run(self, jobInfo):
        # Get working sets
        pointCloudWorkingSet = getWorkingSet(DanesfieldStep.GENERATE_POINT_CLOUD, jobInfo)
        dtmWorkingSet = getWorkingSet(DanesfieldStep.FIT_DTM, jobInfo)
        buildingSegmentationWorkingSet = getWorkingSet(
            DanesfieldStep.UNET_SEMANTIC_SEGMENTATION, jobInfo)

        # Get point cloud file
        pointCloudFile = self.getSingleFile(pointCloudWorkingSet, isPointCloud)

        # Get DTM
        dtmFile = self.getSingleFile(dtmWorkingSet)

        # Get building mask
        buildingMaskFiles = self.getFiles(buildingSegmentationWorkingSet, isClsImage)
        if not buildingMaskFiles:
            raise DanesfieldWorkflowException('Unable to find building mask', step=self.name)
        buildingMaskFile = buildingMaskFiles[0]

        # Get options
        roofGeonExtractionOptions = getOptions(self.name, jobInfo)

        # Run algorithm
        roofGeonExtraction(
            stepName=self.name, requestInfo=jobInfo.requestInfo, jobId=jobInfo.jobId,
            outputFolder=jobInfo.outputFolder, pointCloudFile=pointCloudFile, dtmFile=dtmFile,
            buildingMaskFile=buildingMaskFile, **roofGeonExtractionOptions)
