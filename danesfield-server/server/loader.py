#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
###############################################################################


from girder import events

from .rest import dataset, workingSet, processing, filter

from .event_handlers import onFinalizeUpload, onJobUpdate
from .workflow import DanesfieldWorkflow
from .workflow_manager import DanesfieldWorkflowManager
from .client_webroot import ClientWebroot

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
    events.bind('model.file.finalizeUpload.after', info['name'], onFinalizeUpload)
    events.bind('jobs.job.update', info['name'], onJobUpdate)

    # Set workflow on workflow manager
    DanesfieldWorkflowManager.instance().workflow = createWorkflow()

    # Relocate Girder
    info['serverRoot'], info['serverRoot'].girder = (ClientWebroot(),
                                                     info['serverRoot'])
    # Relocate Girder API
    info['serverRoot'].api = info['serverRoot'].girder.api

    # Add API routes
    info['apiRoot'].dataset = dataset.DatasetResource()
    info['apiRoot'].workingSet = workingSet.WorkingSetResource()
    info['apiRoot'].filter = filter.FilterResource()
    info['apiRoot'].processing = processing.ProcessingResource()
