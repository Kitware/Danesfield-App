#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
###############################################################################

import re

from girder.models.item import Item
from ..algorithms import classifyMaterials
from ..constants import DanesfieldStep
from ..settings import PluginSettings
from ..workflow_step import DanesfieldWorkflowStep
from ..workflow_utilities import (
    getOptions,
    getWorkingSet,
    isMsiImage,
    isMsiNitfMetadata,
)
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
        super(ClassifyMaterialsStep, self).__init__(DanesfieldStep.CLASSIFY_MATERIALS)
        self.addDependency(DanesfieldStep.ORTHORECTIFY)

    def run(self, jobInfo, outputFolder):
        # Get working sets
        initWorkingSet = getWorkingSet(DanesfieldStep.INIT, jobInfo)
        orthorectifyWorkingSet = getWorkingSet(DanesfieldStep.ORTHORECTIFY, jobInfo)

        # Get MSI images
        imageFiles = self.getFiles(orthorectifyWorkingSet, isMsiImage)

        # Get NITF metadata files
        metadataFiles = self.getFiles(initWorkingSet, isMsiNitfMetadata)

        pairs = {}
        for f in imageFiles:
            prefix = getPrefix(f["name"])
            if prefix not in pairs:
                pairs[prefix] = {}

            pairs[prefix]["img"] = f

        for f in metadataFiles:
            prefix = getPrefix(f["name"])
            if prefix not in pairs:
                pairs[prefix] = {}

            pairs[prefix]["meta"] = f

        # Order and select image / metadata files based on the prefix,
        # only including pairs where we have both an image and
        # metadata
        pairedImageFiles = []
        pairedMetadataFiles = []
        for prefix, pair in pairs.items():
            if "img" in pair and "meta" in pair:
                pairedImageFiles.append(pair["img"])
                pairedMetadataFiles.append(pair["meta"])

        # if len(pairedImageFiles) >= 20:
        #     modelVariant = "20"
        #     batchSize = 5000
        # else:
        #     modelVariant = "01"
        #     batchSize = 60000

        # Explicitly using the "01" model variants for now, as the
        # "20" runs out of GPU memory too easily.
        modelVariant = "01"
        batchSize = 60000

        # Get options; Set a reasonable batch size based on model
        # selection unless explicitly set in the options JSON
        classifyMaterialsOptions = getOptions(self.name, jobInfo)
        if "batchSize" not in classifyMaterialsOptions:
            classifyMaterialsOptions["batchSize"] = batchSize

        # Model selection
        model = classifyMaterialsOptions.get("model")

        # Special case for "STANDARD" default model
        if model == "STANDARD":
            modelName = "modelALL_%s.pth.tar" % modelVariant
        else:
            modelName = "model_%s_%s.pth.tar" % (model, modelVariant)

        # Find the right model
        modelFolder = self.getFolderFromSetting(
            PluginSettings.MATERIAL_CLASSIFIER_MODEL_FOLDER_ID
        )
        modelItemRecord = Item().findOne(
            {"folderId": modelFolder["_id"], "name": modelName}
        )

        # Should only be one file in the item
        modelFile = Item().childFiles(modelItemRecord, limit=1)[0]

        # Set outfile prefix; replacing whitespace with underscores
        outfilePrefix = re.sub("\\s", "_", initWorkingSet["name"])

        # Run algorithm
        classifyMaterials(
            initWorkingSetName=initWorkingSet["name"],
            stepName=self.name,
            requestInfo=jobInfo.requestInfo,
            jobId=jobInfo.jobId,
            outputFolder=outputFolder,
            imageFiles=pairedImageFiles,
            metadataFiles=pairedMetadataFiles,
            modelFile=modelFile,
            outfilePrefix=outfilePrefix,
            **classifyMaterialsOptions
        )
