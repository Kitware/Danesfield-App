#!/usr/bin/env python
# -*- coding: utf-8 -*-

##############################################################################
#  Copyright Kitware Inc.
#
#  Licensed under the Apache License, Version 2.0 ( the "License" );
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
##############################################################################

import json

from girder.models.item import Item

from .constants import DanesfieldJobKey


def onFinalizeUpload(event):
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
