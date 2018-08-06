#!/usr/bin/env python
# -*- coding: utf-8 -*-

from girder import events

from rest import dataset, workingSet, processing, filter

from . import workflow_handlers
from .constants import DanesfieldStep
from .event_handlers import onFinalizeUpload, onJobUpdate
from .workflow import DanesfieldWorkflow
from .workflow_manager import DanesfieldWorkflowManager


def load(info):
    # Install event handlers
    events.bind('model.file.finalizeUpload.after', info['name'], onFinalizeUpload)
    events.bind('jobs.job.update', info['name'], onJobUpdate)

    # Configure Danesfield workflow
    workflow = DanesfieldWorkflow()
    workflow.addHandler(DanesfieldStep.INIT, workflow_handlers.runGeneratePointCloud)
    workflow.addHandler(DanesfieldStep.GENERATE_POINT_CLOUD, workflow_handlers.runGenerateDsm)
    workflow.addHandler(DanesfieldStep.GENERATE_DSM, workflow_handlers.runFitDtm)
    workflow.addHandler(DanesfieldStep.FIT_DTM, workflow_handlers.runOrthorectify)
    workflow.addHandler(DanesfieldStep.ORTHORECTIFY, workflow_handlers.runPansharpen)
    workflow.addHandler(DanesfieldStep.PANSHARPEN, workflow_handlers.runMsiToRgb)
    workflow.addHandler(DanesfieldStep.MSI_TO_RGB, workflow_handlers.runFinalize)
    DanesfieldWorkflowManager.instance().workflow = workflow

    # Relocate Girder API
    info['serverRoot'].girder = info['serverRoot']
    info['serverRoot'].api = info['serverRoot'].girder.api

    # Add API routes
    info['apiRoot'].dataset = dataset.DatasetResource()
    info['apiRoot'].workingSet = workingSet.WorkingSetResource()
    info['apiRoot'].filter = filter.FilterResource()
    info['apiRoot'].processing = processing.ProcessingResource()
