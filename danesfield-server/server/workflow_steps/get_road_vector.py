#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
###############################################################################



from ..algorithms import getRoadVector
from ..constants import DanesfieldStep
from ..workflow import DanesfieldWorkflowException
from ..workflow_step import DanesfieldWorkflowStep
from ..workflow_utilities import getOptions, getWorkingSet


class GetRoadVectorStep(DanesfieldWorkflowStep):
    """
    Step that runs p3d to generate a point cloud.

    Supports the following options:
    - left (required)
    - bottom (required)
    - right (required)
    - left (required)
    """
    def __init__(self):
        super(GetRoadVectorStep, self).__init__(DanesfieldStep.GET_ROAD_VECTOR)

    def run(self, jobInfo, outputFolder):
        # Get working sets
        initWorkingSet = getWorkingSet(DanesfieldStep.INIT, jobInfo)

        # Get required options
        getRoadVectorOptions = getOptions(self.name, jobInfo)

        try:
            left = getRoadVectorOptions['left']
            bottom = getRoadVectorOptions['bottom']
            right = getRoadVectorOptions['right']
            top = getRoadVectorOptions['top']
        except KeyError:
            raise DanesfieldWorkflowException(
                'The following options are required: left, bottom, right, '
                'top', step=self.name)

        # Run algorithm
        getRoadVector(
            initWorkingSetName=initWorkingSet['name'],
            stepName=self.name,
            requestInfo=jobInfo.requestInfo,
            jobId=jobInfo.jobId,
            outputFolder=outputFolder,
            left=left,
            bottom=bottom,
            right=right,
            top=top)
