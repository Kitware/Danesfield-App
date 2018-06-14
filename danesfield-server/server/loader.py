#!/usr/bin/env python
# -*- coding: utf-8 -*-

from girder import events

from rest import dataset, workingSet, processing, filter

from .event_handlers import onFinalizeUpload


def load(info):
    # Install event handlers
    events.bind('model.file.finalizeUpload.after', info['name'], onFinalizeUpload)

    # Relocate Girder API
    info['serverRoot'].girder = info['serverRoot']
    info['serverRoot'].api = info['serverRoot'].girder.api

    # Add API routes
    info['apiRoot'].dataset = dataset.DatasetResource()
    info['apiRoot'].workingSet = workingSet.WorkingSetResource()
    info['apiRoot'].filter = filter.FilterResource()
    info['apiRoot'].processing = processing.ProcessingResource()
