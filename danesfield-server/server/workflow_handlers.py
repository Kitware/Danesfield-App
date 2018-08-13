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
from .utilities import hasExtension, isMsiImage, isMsiNitfMetadata, isPanImage
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


def _getWorkingSet(stepName, jobInfo):
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


def _getStandardOutput(stepName, jobInfo):
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


def _getOptions(stepName, jobInfo):
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


def runGeneratePointCloud(requestInfo, jobInfo):
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
    workingSet = _getWorkingSet(DanesfieldStep.INIT, jobInfo)

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
    generatePointCloudOptions = _getOptions(stepName, jobInfo)

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
        stepName=stepName, requestInfo=requestInfo, jobId=jobInfo.jobId, trigger=True,
        outputFolder=jobInfo.outputFolder, imageFileIds=panFileIds,
        longitude=longitude, latitude=latitude,
        longitudeWidth=longitudeWidth, latitudeWidth=latitudeWidth)


def runGenerateDsm(requestInfo, jobInfo):
    """
    Workflow handler to run generate_dsm.

    Supports the following options:
    - <none>
    """
    stepName = DanesfieldStep.GENERATE_DSM

    # Get working sets
    initWorkingSet = _getWorkingSet(DanesfieldStep.INIT, jobInfo)
    pointCloudWorkingSet = _getWorkingSet(DanesfieldStep.GENERATE_POINT_CLOUD, jobInfo)

    # Get point cloud file
    pointCloudItems = [
        item
        for item in (
            Item().load(itemId, force=True, exc=True)
            for itemId in pointCloudWorkingSet['datasetIds']
        )
        if _isPointCloud(item)
    ]
    if not pointCloudItems:
        raise DanesfieldWorkflowException('Unable to find point cloud', step=stepName)
    if len(pointCloudItems) > 1:
        raise DanesfieldWorkflowException(
            'Expected only one point cloud, got {}'.format(len(pointCloudItems)), step=stepName)
    pointCloudFile = _fileFromItem(pointCloudItems[0])

    # Get options
    generateDsmOptions = _getOptions(stepName, jobInfo)

    # Run algorithm
    algorithms.generateDsm(
        stepName=stepName, requestInfo=requestInfo, jobId=jobInfo.jobId, trigger=True,
        outputFolder=jobInfo.outputFolder, file=pointCloudFile,
        outputPrefix=initWorkingSet['name'], **generateDsmOptions)


def runFitDtm(requestInfo, jobInfo):
    """
    Workflow handler to run fit_dtm.

    Supports the following options:
    - iterations
    - tension
    """
    stepName = DanesfieldStep.FIT_DTM

    # Get working sets
    initWorkingSet = _getWorkingSet(DanesfieldStep.INIT, jobInfo)
    dsmWorkingSet = _getWorkingSet(DanesfieldStep.GENERATE_DSM, jobInfo)

    # Get DSM
    items = [Item().load(itemId, force=True, exc=True)
             for itemId in dsmWorkingSet['datasetIds']]
    if not items:
        raise DanesfieldWorkflowException('Unable to find DSM', step=stepName)
    if len(items) > 1:
        raise DanesfieldWorkflowException(
            'Expected only one input file, got {}'.format(len(items)), step=stepName)
    file = _fileFromItem(items[0])

    # Get options
    fitDtmOptions = _getOptions(stepName, jobInfo)

    # Run algorithm
    algorithms.fitDtm(
        stepName=stepName, requestInfo=requestInfo, jobId=jobInfo.jobId, trigger=True,
        outputFolder=jobInfo.outputFolder, file=file, outputPrefix=initWorkingSet['name'],
        **fitDtmOptions)


def runOrthorectify(requestInfo, jobInfo):
    """
    Workflow handler to run orthorectify.

    Supports the following options:
    - occlusionThreshold
    - denoiseRadius
    """
    stepName = DanesfieldStep.ORTHORECTIFY

    # Get working sets
    initWorkingSet = _getWorkingSet(DanesfieldStep.INIT, jobInfo)
    dsmWorkingSet = _getWorkingSet(DanesfieldStep.GENERATE_DSM, jobInfo)
    dtmWorkingSet = _getWorkingSet(DanesfieldStep.FIT_DTM, jobInfo)
    pointCloudWorkingSet = _getWorkingSet(DanesfieldStep.GENERATE_POINT_CLOUD, jobInfo)

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
    orthorectifyOptions = _getOptions(stepName, jobInfo)

    # Run algorithm
    algorithms.orthorectify(
        stepName=stepName, requestInfo=requestInfo, jobId=jobInfo.jobId, trigger=True,
        outputFolder=jobInfo.outputFolder, imageFiles=imageFiles, dsmFile=dsmFile,
        dtmFile=dtmFile, rpcFiles=rpcFiles, **orthorectifyOptions)


def runPansharpen(requestInfo, jobInfo):
    """
    Workflow handler to run pansharpen.

    Supports the following options:
    - <none>
    """
    stepName = DanesfieldStep.PANSHARPEN

    # Get working set
    workingSet = _getWorkingSet(DanesfieldStep.ORTHORECTIFY, jobInfo)

    # Get IDs of MSI and PAN source image files
    imageFiles = [
        _fileFromItem(item)
        for item in (
            Item().load(itemId, force=True, exc=True)
            for itemId in workingSet['datasetIds']
        )
        if isMsiImage(item) or isPanImage(item)
    ]

    # Get options
    pansharpenOptions = _getOptions(stepName, jobInfo)

    # Run algorithm
    algorithms.pansharpen(
        stepName=stepName, requestInfo=requestInfo, jobId=jobInfo.jobId, trigger=True,
        outputFolder=jobInfo.outputFolder, imageFiles=imageFiles, **pansharpenOptions)


def runMsiToRgb(requestInfo, jobInfo):
    """
    Workflow handler to run multispectral image (MSI) to RGB conversion.

    Supports the following options:
    - byte
    - alpha
    - rangePercentile
    """
    stepName = DanesfieldStep.MSI_TO_RGB

    # Get working set
    workingSet = _getWorkingSet(DanesfieldStep.PANSHARPEN, jobInfo)

    # Get IDs of pansharpened MSI images
    imageFiles = [
        _fileFromItem(item)
        for item in (
            Item().load(itemId, force=True, exc=True)
            for itemId in workingSet['datasetIds']
        )
    ]

    # Get options
    msiToRgbOptions = _getOptions(stepName, jobInfo)

    # Run algorithm
    algorithms.convertMsiToRgb(
        stepName=stepName, requestInfo=requestInfo, jobId=jobInfo.jobId, trigger=True,
        outputFolder=jobInfo.outputFolder, imageFiles=imageFiles, **msiToRgbOptions)


def runSegmentByHeight(requestInfo, jobInfo):
    """
    Workflow handler to run segment by height.

    Supports the following options:
    - <none>
    """
    stepName = DanesfieldStep.SEGMENT_BY_HEIGHT

    # Get working sets
    dsmWorkingSet = _getWorkingSet(DanesfieldStep.GENERATE_DSM, jobInfo)
    dtmWorkingSet = _getWorkingSet(DanesfieldStep.FIT_DTM, jobInfo)
    pansharpenWorkingSet = _getWorkingSet(DanesfieldStep.PANSHARPEN, jobInfo)

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

    # Get the ID of the first pansharpened MSI image
    # TODO: Choose most nadir image, likely determined by a previous step and a new tool based on
    # metadata in the source PAN images
    items = [Item().load(itemId, force=True, exc=True)
             for itemId in pansharpenWorkingSet['datasetIds']]
    if not items:
        raise DanesfieldWorkflowException('Unable to find pansharpened images', step=stepName)
    msiImageFile = _fileFromItem(items[0])

    # Get options
    segmentByHeightOptions = _getOptions(stepName, jobInfo)

    # Run algorithm
    algorithms.segmentByHeight(
        stepName=stepName, requestInfo=requestInfo, jobId=jobInfo.jobId, trigger=True,
        outputFolder=jobInfo.outputFolder, dsmFile=dsmFile, dtmFile=dtmFile,
        msiImageFile=msiImageFile, **segmentByHeightOptions)


def runClassifyMaterials(requestInfo, jobInfo):
    """
    Workflow handler to run material classification.

    Supports the following options:
    - cuda
    - batchSize
    """
    stepName = DanesfieldStep.CLASSIFY_MATERIALS

    # Get working sets
    initWorkingSet = _getWorkingSet(DanesfieldStep.INIT, jobInfo)
    orthorectifyWorkingSet = _getWorkingSet(DanesfieldStep.ORTHORECTIFY, jobInfo)

    # Get IDs of MSI images
    imageFiles = [
        _fileFromItem(item)
        for item in (
            Item().load(itemId, force=True, exc=True)
            for itemId in orthorectifyWorkingSet['datasetIds']
        )
        if isMsiImage(item)
    ]

    # Get IDs of NITF metadata files
    metadataFiles = [
        _fileFromItem(item)
        for item in (
            Item().load(itemId, force=True, exc=True)
            for itemId in initWorkingSet['datasetIds']
        )
        if isMsiNitfMetadata(item)
    ]

    # Get options
    classifyMaterialsOptions = _getOptions(stepName, jobInfo)

    # Run algorithm
    algorithms.classifyMaterials(
        stepName=stepName, requestInfo=requestInfo, jobId=jobInfo.jobId, trigger=True,
        outputFolder=jobInfo.outputFolder, imageFiles=imageFiles, metadataFiles=metadataFiles,
        **classifyMaterialsOptions)


def runFinalize(requestInfo, jobInfo):
    """
    Workflow handler to run finalize step.
    """
    algorithms.finalize(requestInfo=requestInfo, jobId=jobInfo.jobId)
