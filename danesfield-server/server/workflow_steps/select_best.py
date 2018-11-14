#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
###############################################################################



import os

from ..algorithms import selectBest
from ..constants import DanesfieldStep
from ..utilities import getPrefix
from ..workflow_step import DanesfieldWorkflowStep
from ..workflow_utilities import getOptions, getWorkingSet, isPanImage


class SelectBestStep(DanesfieldWorkflowStep):
    """
    Step that runs select_best.

    Supports the following options:
    - <none>
    """
    def __init__(self):
        super(SelectBestStep, self).__init__(DanesfieldStep.SELECT_BEST)
        self.addDependency(DanesfieldStep.GENERATE_DSM)

    def run(self, jobInfo, outputFolder):
        # Get working sets
        initWorkingSet = getWorkingSet(DanesfieldStep.INIT, jobInfo)
        dsmWorkingSet = getWorkingSet(DanesfieldStep.GENERATE_DSM, jobInfo)

        # TODO: check PAN vs MSI
        # Get PAN source image files
        imageFiles = self.getFiles(initWorkingSet, isPanImage)

        # Get DSM
        dsmFile = self.getSingleFile(dsmWorkingSet)

        # Get options
        selectBestOptions = getOptions(self.name, jobInfo)

        # Run algorithm
        selectBest(
            initWorkingSetName=initWorkingSet['name'],
            stepName=self.name, requestInfo=jobInfo.requestInfo, jobId=jobInfo.jobId,
            outputFolder=outputFolder, imageFiles=imageFiles, dsmFile=dsmFile,
            **selectBestOptions)

    @staticmethod
    def getImagePrefixes(output):
        """
        Parse output from select_best and return generator of image prefixes.
        Output argument is a list of strings, where each string may contain
        multiple lines.
        """
        prefix = None
        for group in output:
            lines = group.splitlines()
            for line in lines:
                filename = os.path.basename(line)
                prefix = getPrefix(filename)
                if prefix is not None:
                    yield prefix
