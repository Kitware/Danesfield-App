#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

from girder import events
from girder.models.item import Item

from rest import dataset, workingSet, processing, filter

from .constants import DanesfieldJobKey


def _onFinalizeUpload(event):
    """Event handler for finalize upload event."""
    upload = event.info['upload']

    try:
        reference = json.loads(upload.get('reference'))
    except (TypeError, ValueError):
        return

    if not isinstance(reference, dict) or DanesfieldJobKey.SOURCE not in reference:
        return

    source = reference[DanesfieldJobKey.SOURCE]
    # Record source algorithm in metadata
    file = event.info['file']
    item = Item().load(file['itemId'], force=True, exc=True)
    Item().setMetadata(item, {
        'danesfieldSource': source
    })


def load(info):
    # Install event handlers
    events.bind('model.file.finalizeUpload.after', info['name'], _onFinalizeUpload)

    # Relocate Girder API
    info['serverRoot'].girder = info['serverRoot']
    info['serverRoot'].api = info['serverRoot'].girder.api

    # Add API routes
    info['apiRoot'].dataset = dataset.DatasetResource()
    info['apiRoot'].workingSet = workingSet.WorkingSetResource()
    info['apiRoot'].filter = filter.FilterResource()
    info['apiRoot'].processing = processing.ProcessingResource()
