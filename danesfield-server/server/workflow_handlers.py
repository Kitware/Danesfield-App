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

from girder.models.folder import Folder
from girder.models.item import Item

from .algorithms import fitDtm, generateDsm
from .workflow import DanesfieldWorkflowException


def _getFolder(file):
    """Helper function to get the folder in which a file is located."""
    item = Item().load(file['itemId'], force=True, exc=True)
    folder = Folder().load(item['folderId'], force=True, exc=True)
    return folder


def runGenerateDsm(user, apiUrl, token, files):
    """Workflow handler to run generate_dsm."""
    if len(files) > 1:
        raise DanesfieldWorkflowException('Expected only one input file, got {}'.format(len(files)))
    file = files[0]
    outputFolder = _getFolder(file)
    generateDsm(user=user, apiUrl=apiUrl, token=token, trigger=True, file=file,
                outputFolder=outputFolder)


def runFitDtm(user, apiUrl, token, files):
    """Workflow handler to run fit_dtm."""
    if len(files) > 1:
        raise DanesfieldWorkflowException('Expected only one input file, got {}'.format(len(files)))
    file = files[0]
    outputFolder = _getFolder(file)
    fitDtm(user=user, apiUrl=apiUrl, token=token, trigger=True, file=file,
           outputFolder=outputFolder)
