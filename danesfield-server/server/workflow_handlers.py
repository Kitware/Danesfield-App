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

from girder.models.item import Item

from . import algorithms
from .constants import DanesfieldStep
from .utilities import hasExtension, isMsiImage, isPanImage
from .workflow import DanesfieldWorkflowException


def _fileFromItem(item):
    """
    Return the file contained in an item. Raise an exception if the item doesn't contain
    exactly one file.
    """
    files = Item().childFiles(item, limit=2)
    if files.count() != 1:
        raise DanesfieldWorkflowException(
            'Item must contain %d files, but should contain only one.' % files.count())
    return files[0]


def _isPointCloud(item):
    """
    Return true if the item refers to a point cloud.

    :param item: Item document.
    :type item: dict
    """
    return hasExtension(item, '.las')


def _isRpc(item):
    """
    Return true if the item refers to an RPC file.

    :param item: Item document.
    :type item: dict
    """
    return hasExtension(item, '.rpc')


def _getWorkingSet(name, workingSets):
    """
    Get a specific working set by name. Raise an error if the working set is not found.

    :param name: The name of the working set.
    :type name: str
    :param workingSets: The available working sets.
    :type workingSets: dict
    """
    workingSet = workingSets.get(name)
    if workingSet is None:
        raise DanesfieldWorkflowException('Error looking up working set \'{}\''.format(name))
    return workingSet


def runGeneratePointCloud(requestInfo, jobId, workingSets, outputFolder, options):
    """
    Workflow handler to run p3d to generate a point cloud.

    Supports the following options:
    - longitude (required)
    - latitude (required)
    - longitudeWidth (required)
    - latitudeWidth (required)
    """
    stepName = DanesfieldStep.GENERATE_POINT_CLOUD

    # Get working set
    workingSet = _getWorkingSet(DanesfieldStep.INIT, workingSets)

    # Get IDs of PAN image files
    panFileIds = [
        _fileFromItem(item)['_id']
        for item in (
            Item().load(itemId, force=True, exc=True)
            for itemId in workingSet['datasetIds']
        )
        if isMsiImage(item) or isPanImage(item)
    ]

    # Get required options
    generatePointCloudOptions = options.get(stepName)
    if generatePointCloudOptions is None or not isinstance(generatePointCloudOptions, dict):
        raise DanesfieldWorkflowException('Invalid options', step=stepName)

    try:
        longitude = generatePointCloudOptions['longitude']
        latitude = generatePointCloudOptions['latitude']
        longitudeWidth = generatePointCloudOptions['longitudeWidth']
        latitudeWidth = generatePointCloudOptions['latitudeWidth']
    except KeyError:
        raise DanesfieldWorkflowException(
            'The following options are required: longtitude, latitude, longitudewith, '
            'latitudeWidth', step=stepName)

    # Run algorithm
    algorithms.generatePointCloud(
        stepName=stepName, requestInfo=requestInfo, jobId=jobId, trigger=True,
        outputFolder=outputFolder, imageFileIds=panFileIds,
        longitude=longitude, latitude=latitude,
        longitudeWidth=longitudeWidth, latitudeWidth=latitudeWidth)


def runGenerateDsm(requestInfo, jobId, workingSets, outputFolder, options):
    """
    Workflow handler to run generate_dsm.
    """
    stepName = DanesfieldStep.GENERATE_DSM

    # Get working set
    workingSet = _getWorkingSet(DanesfieldStep.GENERATE_POINT_CLOUD, workingSets)

    # Get point cloud file
    pointCloudItems = [
        item
        for item in (
            Item().load(itemId, force=True, exc=True)
            for itemId in workingSet['datasetIds']
        )
        if _isPointCloud(item)
    ]
    if not pointCloudItems:
        raise DanesfieldWorkflowException('Unable to find point cloud', step=stepName)
    if len(pointCloudItems) > 1:
        raise DanesfieldWorkflowException(
            'Expected only one point cloud, got {}'.format(len(pointCloudItems)), step=stepName)
    pointCloudFile = _fileFromItem(pointCloudItems[0])

    # Run algorithm
    algorithms.generateDsm(
        stepName=stepName, requestInfo=requestInfo, jobId=jobId, trigger=True,
        outputFolder=outputFolder, file=pointCloudFile)


def runFitDtm(requestInfo, jobId, workingSets, outputFolder, options):
    """
    Workflow handler to run fit_dtm.

    Supports the following options:
    - iterations
    - tension
    """
    stepName = DanesfieldStep.FIT_DTM

    # Get working set
    workingSet = _getWorkingSet(DanesfieldStep.GENERATE_DSM, workingSets)

    # Get DSM
    items = [Item().load(itemId, force=True, exc=True)
             for itemId in workingSet['datasetIds']]
    if not items:
        raise DanesfieldWorkflowException('Unable to find DSM', step=stepName)
    if len(items) > 1:
        raise DanesfieldWorkflowException(
            'Expected only one input file, got {}'.format(len(items)), step=stepName)
    file = _fileFromItem(items[0])

    # Get options
    fitDtmOptions = options.get(stepName, {})
    if not isinstance(fitDtmOptions, dict):
        raise DanesfieldWorkflowException('Invalid options', step=stepName)

    # Run algorithm
    algorithms.fitDtm(
        stepName=stepName, requestInfo=requestInfo, jobId=jobId, trigger=True,
        outputFolder=outputFolder, file=file, **fitDtmOptions)


def runOrthorectify(requestInfo, jobId, workingSets, outputFolder, options):
    """
    Workflow handler to run orthorectify.

    Supports the following options:
    - occlusionThreshold
    - denoiseRadius
    """
    stepName = DanesfieldStep.ORTHORECTIFY

    # Get working sets
    initWorkingSet = _getWorkingSet(DanesfieldStep.INIT, workingSets)
    dsmWorkingSet = _getWorkingSet(DanesfieldStep.GENERATE_DSM, workingSets)
    dtmWorkingSet = _getWorkingSet(DanesfieldStep.FIT_DTM, workingSets)
    pointCloudWorkingSet = _getWorkingSet(DanesfieldStep.GENERATE_POINT_CLOUD, workingSets)

    # Get IDs of MSI and PAN source image files
    imageFiles = [
        _fileFromItem(item)
        for item in (
            Item().load(itemId, force=True, exc=True)
            for itemId in initWorkingSet['datasetIds']
        )
        if isMsiImage(item) or isPanImage(item)
    ]

    # Get DSM
    items = [Item().load(itemId, force=True, exc=True)
             for itemId in dsmWorkingSet['datasetIds']]
    if not items:
        raise DanesfieldWorkflowException('Unable to find DSM', step=stepName)
    if len(items) > 1:
        raise DanesfieldWorkflowException(
            'Expected only one input file, got {}'.format(len(items)), step=stepName)
    dsmFile = _fileFromItem(items[0])

    # Get DTM
    items = [Item().load(itemId, force=True, exc=True)
             for itemId in dtmWorkingSet['datasetIds']]
    if not items:
        raise DanesfieldWorkflowException('Unable to find DTM', step=stepName)
    if len(items) > 1:
        raise DanesfieldWorkflowException(
            'Expected only one input file, got {}'.format(len(items)), step=stepName)
    dtmFile = _fileFromItem(items[0])

    # Get updated RPC files
    rpcFiles = [
        _fileFromItem(item)
        for item in (
            Item().load(itemId, force=True, exc=True)
            for itemId in pointCloudWorkingSet['datasetIds']
        )
        if _isRpc(item)
    ]

    # Get options
    orthorectifyOptions = options.get(stepName, {})
    if not isinstance(orthorectifyOptions, dict):
        raise DanesfieldWorkflowException('Invalid options', step=stepName)

    # Run algorithm
    algorithms.orthorectify(
        stepName=stepName, requestInfo=requestInfo, jobId=jobId, trigger=True,
        outputFolder=outputFolder, imageFiles=imageFiles, dsmFile=dsmFile, dtmFile=dtmFile,
        rpcFiles=rpcFiles, **orthorectifyOptions)


def runFinalize(requestInfo, jobId, workingSets, outputFolder, options):
    """
    Workflow handler to run finalize step.
    """
    algorithms.finalize(requestInfo=requestInfo, jobId=jobId)
