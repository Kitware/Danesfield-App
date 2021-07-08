#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
###############################################################################

from girder import events
from girder.utility.config import getServerMode

from .rest import dataset, workingSet, processing, filter

from .event_handlers import onFinalizeUpload, onJobUpdate
from .workflow import DanesfieldWorkflow
from .workflow_manager import DanesfieldWorkflowManager
from .client_webroot import ClientWebroot

from .workflow_steps import RunDanesfieldImageless


def createWorkflow():
    """
    Configure Danesfield Workflow.
    """
    workflow = DanesfieldWorkflow()

    for step in [
        RunDanesfieldImageless,
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
    # TODO: On each request to /process, set this to either the normal or point-cloud starting workflow?
    DanesfieldWorkflowManager.instance().workflow = createWorkflow()

    if getServerMode() == "production":
        # Serve client from /
        # Relocate girder to serve from /girder
        info["serverRoot"], info["serverRoot"].girder = (
            ClientWebroot(),
            info["serverRoot"],
        )
        info["serverRoot"].api = info["serverRoot"].girder.api

    # Add API routes
    info["apiRoot"].dataset = dataset.DatasetResource()
    info["apiRoot"].workingSet = workingSet.WorkingSetResource()
    info["apiRoot"].filter = filter.FilterResource()
    info["apiRoot"].processing = processing.ProcessingResource()
