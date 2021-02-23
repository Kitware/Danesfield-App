#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
###############################################################################

import os
from girder import events
from girder.utility.config import getServerMode
from girder.models.setting import Setting

from .rest import dataset, workingSet, processing, filter

from .event_handlers import onFinalizeUpload, onJobUpdate
from .workflow import DanesfieldWorkflow
from .workflow_manager import DanesfieldWorkflowManager
from .client_webroot import ClientWebroot
from .settings import PluginSettings

from .workflow_steps import (
    # BuildingSegmentationStep,
    ClassifyMaterialsStep,
    FitDtmStep,
    GenerateDsmStep,
    GeneratePointCloudStep,
    # MsiToRgbStep,
    OrthorectifyStep,
    # PansharpenStep,
    RoofGeonExtractionStep,
    ComputeNdviStep,
    SegmentByHeightStep,
    # SelectBestStep,
    # UNetSemanticSegmentationStep,
    BuildingsToDsmStep,
    GetRoadVectorStep,
    CropAndPansharpenStep,
    TextureMappingStep,
    RunMetricsStep,
)


def createWorkflow():
    """
    Configure Danesfield Workflow.
    """
    workflow = DanesfieldWorkflow()

    for step in [
        # BuildingSegmentationStep,
        ClassifyMaterialsStep,
        FitDtmStep,
        GenerateDsmStep,
        GeneratePointCloudStep,
        # MsiToRgbStep,
        OrthorectifyStep,
        # PansharpenStep,
        RoofGeonExtractionStep,
        ComputeNdviStep,
        SegmentByHeightStep,
        # SelectBestStep,
        # UNetSemanticSegmentationStep,
        BuildingsToDsmStep,
        GetRoadVectorStep,
        CropAndPansharpenStep,
        TextureMappingStep,
        RunMetricsStep,
    ]:
        workflow.addStep(step())

    return workflow


def load(info):
    # Install event handlers
    events.bind(
        "model.file.finalizeUpload.after", "danesfield-after-upload", onFinalizeUpload
    )
    events.bind("jobs.job.update", "danesfield-job-update", onJobUpdate)

    # Set workflow on workflow manager
    DanesfieldWorkflowManager.instance().workflow = createWorkflow()

    if getServerMode() == "production":
        # Serve client from /
        # Relocate girder to serve from /girder
        info["serverRoot"], info["serverRoot"].girder = (
            ClientWebroot(),
            info["serverRoot"],
        )
        info["serverRoot"].api = info["serverRoot"].girder.api

    host_gtopo30_data_path = os.getenv("HOST_GTOPO30_DATA_PATH")
    if host_gtopo30_data_path:
        Setting().set(PluginSettings.HOST_GTOPO30_DATA_PATH, host_gtopo30_data_path)

    # Add API routes
    info["apiRoot"].dataset = dataset.DatasetResource()
    info["apiRoot"].workingSet = workingSet.WorkingSetResource()
    info["apiRoot"].filter = filter.FilterResource()
    info["apiRoot"].processing = processing.ProcessingResource()
