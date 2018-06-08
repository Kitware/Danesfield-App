#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

from girder import events
from girder.models.item import Item

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
