#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
###############################################################################

from ..algorithms import generatePointCloud
from ..constants import DanesfieldStep
from ..workflow import DanesfieldWorkflowException
from ..workflow_step import DanesfieldWorkflowStep
from ..workflow_utilities import getOptions, getWorkingSet, isPanImage


class GeneratePointCloudStep(DanesfieldWorkflowStep):
    """
    Step that generates a point cloud.

    Supports the following options:
    - aoiBBox (required)
    """

    def __init__(self):
        super(GeneratePointCloudStep, self).__init__(
            DanesfieldStep.GENERATE_POINT_CLOUD
        )

    def run(self, jobInfo, outputFolder):
        # Get working set
        initWorkingSet = getWorkingSet(DanesfieldStep.INIT, jobInfo)

        def isTarFile(item):
            return item["name"].endswith(".tar")

        # Get IDs of PAN image files
        fileNameDict = {}
        workingSetFiles = self.getFiles(initWorkingSet)
        for file in workingSetFiles:
            baseFileName = file["name"].split(".")[0]

            if not fileNameDict.get(baseFileName):
                fileNameDict[baseFileName] = [None, None]

            if isPanImage(file):
                fileNameDict[baseFileName][0] = file
            elif isTarFile(file):
                fileNameDict[baseFileName][1] = file

        filePairs = [tuple(pair) for pair in fileNameDict.values() if all(pair)]

        # Get required options
        generatePointCloudOptions = getOptions(self.name, jobInfo)

        try:
            aoiBBox = generatePointCloudOptions["aoiBBox"]
        except KeyError:
            raise DanesfieldWorkflowException(
                "The following options are required: aoiBBox",
                step=self.name,
            )

        # Run algorithm
        generatePointCloud(
            initWorkingSetName=initWorkingSet["name"],
            stepName=self.name,
            requestInfo=jobInfo.requestInfo,
            jobId=jobInfo.jobId,
            outputFolder=outputFolder,
            filePairs=filePairs,
            aoiBBox=aoiBBox,
        )
