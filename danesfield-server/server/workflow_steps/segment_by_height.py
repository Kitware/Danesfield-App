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

from girder.models.folder import Folder

from .select_best import SelectBestStep
from ..algorithms import segmentByHeight
from ..constants import DanesfieldStep
from ..settings import PluginSettings
from ..utilities import getPrefix
from ..workflow import DanesfieldWorkflowException
from ..workflow_step import DanesfieldWorkflowStep
from ..workflow_utilities import getOptions, getStandardOutput, getWorkingSet


class SegmentByHeightStep(DanesfieldWorkflowStep):
    """
    Step that runs segment by height.

    Supports the following options:
    - <none>
    """
    def __init__(self):
        super(SegmentByHeightStep, self).__init__(DanesfieldStep.SEGMENT_BY_HEIGHT)
        self.addDependency(DanesfieldStep.GENERATE_DSM)
        self.addDependency(DanesfieldStep.FIT_DTM)
        self.addDependency(DanesfieldStep.PANSHARPEN)
        self.addDependency(DanesfieldStep.SELECT_BEST)

    def run(self, jobInfo):
        # Get working sets
        dsmWorkingSet = getWorkingSet(DanesfieldStep.GENERATE_DSM, jobInfo)
        dtmWorkingSet = getWorkingSet(DanesfieldStep.FIT_DTM, jobInfo)
        pansharpenWorkingSet = getWorkingSet(DanesfieldStep.PANSHARPEN, jobInfo)

        # Get prefix of best image set
        selectBestStandardOutput = getStandardOutput(DanesfieldStep.SELECT_BEST, jobInfo)
        prefix = next(SelectBestStep.getImagePrefixes(selectBestStandardOutput), None)
        if prefix is None:
            raise DanesfieldWorkflowException('Error looking up best image set', step=self.name)

        # Get DSM
        dsmFile = self.getSingleFile(dsmWorkingSet)

        # Get DTM
        dtmFile = self.getSingleFile(dtmWorkingSet)

        # Get the best pansharpened MSI image
        msiImageFiles = self.getFiles(
            pansharpenWorkingSet,
            lambda item: getPrefix(item['name']) == prefix)
        if not msiImageFiles:
            raise DanesfieldWorkflowException(
                'Unable to find best pansharpened image', step=self.name)
        msiImageFile = msiImageFiles[0]

        # Get options
        segmentByHeightOptions = getOptions(self.name, jobInfo)

        shapefilesFolder = self.getFolderFromSetting(
            PluginSettings.SEGMENT_BY_HEIGHT_SHAPEFILES_FOLDER_ID)

        # Get shapefiles prefix
        shapefiles = list(Folder().childItems(shapefilesFolder, limit=1))
        if not shapefiles:
            raise DanesfieldWorkflowException(
                'Shapefiles for segment by height not found.', step=self.name)
        shapefilePrefix = os.path.splitext(shapefiles[0]['name'])[0]

        # Run algorithm
        segmentByHeight(
            stepName=self.name,
            requestInfo=jobInfo.requestInfo,
            jobId=jobInfo.jobId,
            outputFolder=jobInfo.outputFolder,
            dsmFile=dsmFile,
            dtmFile=dtmFile,
            msiImageFile=msiImageFile,
            shapefilesFolder=shapefilesFolder,
            shapefilePrefix=shapefilePrefix,
            **segmentByHeightOptions)