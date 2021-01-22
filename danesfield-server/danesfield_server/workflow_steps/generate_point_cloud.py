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
from ..workflow_utilities import getOptions, getWorkingSet, isMsiImage, isPanImage


class GeneratePointCloudStep(DanesfieldWorkflowStep):
    """
    Step that runs p3d to generate a point cloud.

    Supports the following options:
    - longitude (required)
    - latitude (required)
    - longitudeWidth (required)
    - latitudeWidth (required)
    """

    def __init__(self):
        super(GeneratePointCloudStep, self).__init__(
            DanesfieldStep.GENERATE_POINT_CLOUD
        )

    def run(self, jobInfo, outputFolder):
        # Get working set
        initWorkingSet = getWorkingSet(DanesfieldStep.INIT, jobInfo)

        # Get IDs of PAN image files
        imageFiles = self.getFiles(
            initWorkingSet, lambda item: isMsiImage(item) or isPanImage(item)
        )

        # Get required options
        generatePointCloudOptions = getOptions(self.name, jobInfo)

        try:
            longitude = generatePointCloudOptions["longitude"]
            latitude = generatePointCloudOptions["latitude"]
            longitudeWidth = generatePointCloudOptions["longitudeWidth"]
            latitudeWidth = generatePointCloudOptions["latitudeWidth"]
        except KeyError:
            raise DanesfieldWorkflowException(
                "The following options are required: longtitude, latitude, "
                "longitudewith, latitudeWidth",
                step=self.name,
            )

        # Run algorithm
        generatePointCloud(
            initWorkingSetName=initWorkingSet["name"],
            stepName=self.name,
            requestInfo=jobInfo.requestInfo,
            jobId=jobInfo.jobId,
            outputFolder=outputFolder,
            imageFiles=imageFiles,
            longitude=longitude,
            latitude=latitude,
            longitudeWidth=longitudeWidth,
            latitudeWidth=latitudeWidth,
        )
