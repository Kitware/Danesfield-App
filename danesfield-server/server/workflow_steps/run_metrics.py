#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
###############################################################################



from ..algorithms import runMetrics
from ..constants import DanesfieldStep
from ..settings import PluginSettings
from ..workflow_step import DanesfieldWorkflowStep
from ..workflow_utilities import (
    getOptions, getWorkingSet, isClsImage, isDsmImage, isMtlImage)


class RunMetricsStep(DanesfieldWorkflowStep):
    """
    Step that runs the pubgeo core3d metrics.
    """

    def __init__(self):
        super(RunMetricsStep, self).__init__(DanesfieldStep.RUN_METRICS)
        self.addDependency(DanesfieldStep.CLASSIFY_MATERIALS)
        self.addDependency(DanesfieldStep.BUILDINGS_TO_DSM)
        self.addDependency(DanesfieldStep.FIT_DTM)

    def run(self, jobInfo, outputFolder):
        # Get working sets
        initWorkingSet = getWorkingSet(DanesfieldStep.INIT, jobInfo)
        classifyMaterialsWorkingSet = getWorkingSet(DanesfieldStep.CLASSIFY_MATERIALS, jobInfo)
        buildingsToDsmWorkingSet = getWorkingSet(DanesfieldStep.BUILDINGS_TO_DSM, jobInfo)
        dtmWorkingSet = getWorkingSet(DanesfieldStep.FIT_DTM, jobInfo)

        runMetricsOptions = getOptions(self.name, jobInfo)
        classifyMaterialsOptions = getOptions(DanesfieldStep.CLASSIFY_MATERIALS, jobInfo)

        # Using the "model" passed through the classify materials
        # options as the reference file prefix for now
        referencePrefix = classifyMaterialsOptions.get('model')

        referenceFolder = self.getFolderFromSetting(
            PluginSettings.REFERENCE_DATA_FOLDER_ID)

        # Get DTM
        dtmFile = self.getSingleFile(dtmWorkingSet)

        # Get CLS
        clsFile = self.getSingleFile(buildingsToDsmWorkingSet, isClsImage)

        # Get DSM
        dsmFile = self.getSingleFile(buildingsToDsmWorkingSet, isDsmImage)

        # Get MTL
        mtlFile = self.getSingleFile(classifyMaterialsWorkingSet, isMtlImage)

        # Run algorithm
        runMetrics(
            initWorkingSetName=initWorkingSet['name'],
            stepName=self.name,
            requestInfo=jobInfo.requestInfo,
            jobId=jobInfo.jobId,
            outputFolder=outputFolder,
            referenceFolder=referenceFolder,
            referencePrefix=referencePrefix,
            dtmFile=dtmFile,
            dsmFile=dsmFile,
            clsFile=clsFile,
            mtlFile=mtlFile,
            **runMetricsOptions)
