#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

from girder import events
from girder.models.item import Item
from girder.plugins.jobs.constants import JobStatus

from rest import dataset, workingSet, processing, filter


def _onFinalizeUpload(event):
    """Event handler for finalize upload event."""
    upload = event.info['upload']

    try:
        reference = json.loads(upload.get('reference'))
    except (TypeError, ValueError):
        return

    if not isinstance(reference, dict) or 'danesfieldSource' not in reference:
        return

    # Record source algorithm in metadata
    file = event.info['file']
    item = Item().load(file['itemId'], force=True, exc=True)
    item['danesfieldSource'] = reference['danesfieldSource']
    Item().setMetadata(item, {
        'danesfieldSource': reference['danesfieldSource']
    })


def _onJobUpdate(event):
    """
    Event handler for job update event.
    Delete output items from canceled or errored Danesfield jobs.
    """
    job = event.info['job']
    params = event.info['params']

    if 'danesfieldSource' not in job:
        return

    try:
        # FIXME: Sometimes status is unicode, not int
        status = int(params['status'])
    except (TypeError, KeyError, ValueError):
        return

    if status not in [JobStatus.CANCELED, JobStatus.ERROR]:
        return

    itemIds = job.get('danesfieldItems')
    if not itemIds:
        return

    for itemId in itemIds:
        item = Item().load(itemId, force=True, exc=True)
        Item().remove(item)


def load(info):
    # Install event handlers
    events.bind('model.file.finalizeUpload.after', info['name'], _onFinalizeUpload)
    events.bind('jobs.job.update', info['name'], _onJobUpdate)

    # Relocate Girder API
    info['serverRoot'].girder = info['serverRoot']
    info['serverRoot'].api = info['serverRoot'].girder.api

    # Add API routes
    info['apiRoot'].dataset = dataset.DatasetResource()
    info['apiRoot'].workingSet = workingSet.WorkingSetResource()
    info['apiRoot'].filter = filter.FilterResource()
    info['apiRoot'].processing = processing.ProcessingResource()
