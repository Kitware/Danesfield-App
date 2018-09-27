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

import re

from girder.models.item import Item
from ..algorithms import classifyMaterials
from ..constants import DanesfieldStep
from ..settings import PluginSettings
from ..workflow_step import DanesfieldWorkflowStep
from ..workflow_utilities import (
    getOptions, getWorkingSet, isMsiImage, isMsiNitfMetadata)
from ..utilities import getPrefix


class ClassifyMaterialsStep(DanesfieldWorkflowStep):
    """
    Step that runs material classification.

    Supports the following options:
    - cuda
    - batchSize
    - model
    """
    def __init__(self):
        super(ClassifyMaterialsStep, self).__init__(
            DanesfieldStep.CLASSIFY_MATERIALS)
        self.addDependency(DanesfieldStep.ORTHORECTIFY)

    def run(self, jobInfo, outputFolder):
        # Get working sets
        initWorkingSet = getWorkingSet(DanesfieldStep.INIT, jobInfo)
        orthorectifyWorkingSet = getWorkingSet(DanesfieldStep.ORTHORECTIFY,
                                               jobInfo)

        # Get MSI images
        imageFiles = self.getFiles(orthorectifyWorkingSet, isMsiImage)

        # Get NITF metadata files
        metadataFiles = self.getFiles(initWorkingSet, isMsiNitfMetadata)

        pairs = {}
        for f in imageFiles:
            prefix = getPrefix(f['name'])
            if prefix not in pairs:
                pairs[prefix] = {}

            pairs[prefix]['img'] = f

        for f in metadataFiles:
            prefix = getPrefix(f['name'])
            if prefix not in pairs:
                pairs[prefix] = {}

            pairs[prefix]['meta'] = f

        pairedImageFiles = []
        pairedMetadataFiles = []
        for prefix, pair in pairs.items():
            if 'img' in pair and 'meta' in pair:
                pairedImageFiles.append(pair['img'])
                pairedMetadataFiles.append(pair['meta'])

        if len(pairedImageFiles) >= 20:
            modelVariant = "20"
        else:
            modelVariant = "01"

        # Get options
        classifyMaterialsOptions = getOptions(self.name, jobInfo)

        # Model selection
        model = classifyMaterialsOptions.get('model')

        # Special case for "STANDARD" default model
        if model == "STANDARD":
            modelName = "modelALL_%s.pth.tar" % modelVariant
        else:
            modelName = "model_%s_%s.pth.tar" % (model, modelVariant)

        # Find the right model
        modelFolder = self.getFolderFromSetting(
            PluginSettings.MATERIAL_CLASSIFIER_MODEL_FOLDER_ID)
        modelItemRecord = Item().findOne({'folderId': modelFolder['_id'],
                                          'name': modelName})

        # Should only be one file in the item
        modelFile = Item().childFiles(modelItemRecord, limit=1)[0]

        # Set outfile prefix; replacing whitespace with underscores
        outfilePrefix = re.sub("\\s", "_", initWorkingSet['name'])

        # Run algorithm
        classifyMaterials(
            initWorkingSetName=initWorkingSet['name'],
            stepName=self.name,
            requestInfo=jobInfo.requestInfo,
            jobId=jobInfo.jobId,
            outputFolder=outputFolder,
            imageFiles=imageFiles,
            metadataFiles=metadataFiles,
            modelFile=modelFile,
            outfilePrefix=outfilePrefix,
            **classifyMaterialsOptions)
