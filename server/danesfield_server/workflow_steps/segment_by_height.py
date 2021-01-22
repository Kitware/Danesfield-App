#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
###############################################################################

from ..algorithms import segmentByHeight
from ..constants import DanesfieldStep
from ..workflow_step import DanesfieldWorkflowStep
from ..workflow_utilities import getOptions, getWorkingSet


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
        self.addDependency(DanesfieldStep.GET_ROAD_VECTOR)
        self.addDependency(DanesfieldStep.COMPUTE_NDVI)

    def run(self, jobInfo, outputFolder):
        # Get working sets
        initWorkingSet = getWorkingSet(DanesfieldStep.INIT, jobInfo)
        dsmWorkingSet = getWorkingSet(DanesfieldStep.GENERATE_DSM, jobInfo)
        dtmWorkingSet = getWorkingSet(DanesfieldStep.FIT_DTM, jobInfo)
        ndviWorkingSet = getWorkingSet(DanesfieldStep.COMPUTE_NDVI, jobInfo)
        getRoadVectorWorkingSet = getWorkingSet(DanesfieldStep.GET_ROAD_VECTOR, jobInfo)

        # Get DSM
        dsmFile = self.getSingleFile(dsmWorkingSet)

        # Get DTM
        dtmFile = self.getSingleFile(dtmWorkingSet)

        # Get Road Vector
        roadVectorFile = self.getSingleFile(
            getRoadVectorWorkingSet, lambda item: item["name"] == "road_vector.geojson"
        )

        # Get NDVI
        ndviFile = self.getSingleFile(ndviWorkingSet)

        # Get options
        segmentByHeightOptions = getOptions(self.name, jobInfo)

        # Run algorithm
        segmentByHeight(
            initWorkingSetName=initWorkingSet["name"],
            stepName=self.name,
            requestInfo=jobInfo.requestInfo,
            jobId=jobInfo.jobId,
            outputFolder=outputFolder,
            dsmFile=dsmFile,
            dtmFile=dtmFile,
            ndviFile=ndviFile,
            roadVectorFile=roadVectorFile,
            **segmentByHeightOptions
        )
