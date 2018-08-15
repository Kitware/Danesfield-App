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

import os

from girder.models.item import Item

from .utilities import hasExtension
from .workflow import DanesfieldWorkflowException


def fileFromItem(item):
    """
    Return the file contained in an item. Raise an exception if the item doesn't contain
    exactly one file.
    """
    files = Item().childFiles(item, limit=2)
    if files.count() != 1:
        raise DanesfieldWorkflowException(
            'Item must contain %d files, but should contain only one.' % files.count())
    return files[0]


def isMsiImage(item):
    """
    Return true if the item refers to an MSI image.

    :param item: Item document.
    :type item: dict
    """
    name = item['name'].lower()
    ext = os.path.splitext(name)[1]
    return '-m1bs-' in name and ext.startswith(('.ntf', '.tif'))


def isPanImage(item):
    """
    Return true if the item refers to a PAN image.

    :param item: Item document.
    :type item: dict
    """
    name = item['name'].lower()
    ext = os.path.splitext(name)[1]
    return '-p1bs-' in name and ext.startswith(('.ntf', '.tif'))


def isMsiNitfMetadata(item):
    """
    Return true if the item refers to an MSI-source NITF metadata file.

    :param item: Item document.
    :type item: dict
    """
    name = item['name'].lower()
    ext = os.path.splitext(name)[1]
    return '-m1bs-' in name and ext.startswith(('.imd', '.tar'))


def isPointCloud(item):
    """
    Return true if the item refers to a point cloud.

    :param item: Item document.
    :type item: dict
    """
    return hasExtension(item, '.las')


def isRpc(item):
    """
    Return true if the item refers to an RPC file.

    :param item: Item document.
    :type item: dict
    """
    return hasExtension(item, '.rpc')


def getWorkingSet(stepName, jobInfo):
    """
    Get a specific working set by step name. Raise an error if the working set is not found.

    :param stepName: The name of the step.
    :type stepName: str (DanesfieldStep)
    :param jobInfo: Danesfield job information.
    :type jobInfo: JobInfo
    """
    workingSet = jobInfo.workingSets.get(stepName)
    if workingSet is None:
        raise DanesfieldWorkflowException(
            'Error looking up working set for step\'{}\''.format(stepName))
    return workingSet


def getStandardOutput(stepName, jobInfo):
    """
    Get a standard output for a specific step by name. Raise an error if the standard output is
    not found.

    :param stepName: The name of the step.
    :type stepName: str (DanesfieldStep)
    :param jobInfo: Danesfield job information.
    :type jobInfo: JobInfo
    """
    standardOutput = jobInfo.standardOutput.get(stepName)
    if standardOutput is None:
        raise DanesfieldWorkflowException(
            'Error looking up standard output \'{}\''.format(stepName))
    return standardOutput


def getOptions(stepName, jobInfo):
    """
    Get the options for a particular step from the global options and perform basic
    validation. Returns a dictionary that may be empty.

    :param stepName: The name of the step.
    :type stepName: str (DanesfieldStep)
    :param jobInfo: Danesfield job information.
    :type jobInfo: JobInfo
    :returns: Options for the specified step.
    """
    options = jobInfo.options.get(stepName, {})
    if not isinstance(options, dict):
        raise DanesfieldWorkflowException('Invalid options', step=stepName)
    return options
