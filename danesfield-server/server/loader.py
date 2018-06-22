#!/usr/bin/env python
# -*- coding: utf-8 -*-

from girder import events

from rest import dataset, workingSet, processing, filter

from .event_handlers import onFinalizeUpload, onJobUpdate
from .workflow import DanesfieldWorkflow
from .workflow_handlers import runFitDtm, runGenerateDsm
from .workflow_manager import DanesfieldWorkflowManager


def load(info):
    # Install event handlers
    events.bind('model.file.finalizeUpload.after', info['name'], onFinalizeUpload)
    events.bind('jobs.job.update', info['name'], onJobUpdate)

    # Configure Danesfield workflow
    workflow = DanesfieldWorkflow()
    workflow.addHandler('p3d', runGenerateDsm)
    workflow.addHandler('generate-dsm', runFitDtm)
    DanesfieldWorkflowManager.instance().workflow = workflow

    # Relocate Girder API
    info['serverRoot'].girder = info['serverRoot']
    info['serverRoot'].api = info['serverRoot'].girder.api

    # Add API routes
    info['apiRoot'].dataset = dataset.DatasetResource()
    info['apiRoot'].workingSet = workingSet.WorkingSetResource()
    info['apiRoot'].filter = filter.FilterResource()
    info['apiRoot'].processing = processing.ProcessingResource()
