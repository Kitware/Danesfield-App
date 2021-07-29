#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
###############################################################################

from danesfield_server.constants import DanesfieldStep
import time

from girder.api import access
from girder.api.describe import autoDescribeRoute, Description
from girder.api.rest import Resource, getApiUrl, getCurrentToken
from girder.models.collection import Collection
from girder.models.folder import Folder
from girder.models.user import User

from ..models.workingSet import WorkingSet
from ..request_info import RequestInfo
from ..workflow_manager import DanesfieldWorkflowManager


class ProcessingResource(Resource):
    """
    API endpoints to run Danesfield algorithm jobs.
    """

    def __init__(self):
        super(ProcessingResource, self).__init__()

        self.resourceName = "processing"

        self.route("POST", ("process",), self.process)
        self.route("POST", ("setPointCloud",), self.setPointCloud)

    def _outputFolder(self, workingSet):
        """
        Return the output folder document. Creates a collection if
        necessary. Creates a folder named by the initial working set
        and a timestamp.
        """
        # FIXME: Folder is accessible only to admin
        adminUser = User().getAdmins().next()
        collection = Collection().createCollection(
            name="core3d",
            creator=adminUser,
            description="",
            public=True,
            reuseExisting=True,
        )

        timestamp = str(time.time()).split(".")[0]
        folderName = "{}-{}".format(workingSet["name"], timestamp)
        folder = Folder().createFolder(
            parent=collection,
            name=folderName,
            parentType="collection",
            public=False,
            creator=adminUser,
        )
        return folder

    @access.user
    @autoDescribeRoute(
        Description("Run the complete processing workflow.")
        .notes(
            """
Call this endpoint to run the complete processing workflow.\n
Options may be provided for individual steps by passing a JSON object
in the **options** parameter. For example:\n
```
{
    "generate-point-cloud": {
        "longitude": -84.084032161833051,
        "latitude": 39.780404255857590,
        "longitudeWidth": 0.008880209782049,
        "latitudeWidth": 0.007791684155826
    },
    "fit-dtm": {
        "iterations": 100,
        "tension": 10
    },
    "orthorectify": {
        "occlusionThreshold": 1.0,
        "denoiseRadius": 2.0
    }
}
```
"""
        )
        .modelParam(
            "workingSet",
            "The ID of the working set.",
            model=WorkingSet,
            paramType="query",
        )
        .jsonParam(
            "options",
            "Processing options keyed by step name.",
            requireObject=True,
            required=False,
        )
        .errorResponse()
        .errorResponse("Read access was denied on the item.", 403)
    )
    def process(self, workingSet, options, params):
        """
        Run the complete processing workflow.
        """
        user = self.getCurrentUser()
        apiUrl = getApiUrl()
        token = getCurrentToken()
        outputFolder = self._outputFolder(workingSet)

        requestInfo = RequestInfo(user=user, apiUrl=apiUrl, token=token)

        workflowManager = DanesfieldWorkflowManager.instance()
        jobId = workflowManager.initJob(requestInfo, workingSet, outputFolder, options)
        workflowManager.advance(jobId=jobId)

    @access.user
    @autoDescribeRoute(
        Description(
            "Set the point cloud file (by supplying an item ID)"
            " for the imageless workflow, after upload"
        )
        .modelParam(
            "workingSet",
            "The ID of the working set.",
            model=WorkingSet,
            paramType="query",
        )
        .param(
            "itemId",
            "The ID of the item containing the point cloud file.",
            required=True,
        )
    )
    def setPointCloud(self, workingSet, itemId):
        workingSetName = f"{workingSet['name']}: {DanesfieldStep.GENERATE_POINT_CLOUD}"
        existingWorkingSet = WorkingSet().findOne({"name": workingSetName})
        if existingWorkingSet is not None:
            existingWorkingSet["datasetIds"] = [itemId]
            WorkingSet().save(existingWorkingSet)
            return

        # Create otherwise
        WorkingSet().createWorkingSet(
            name=workingSetName,
            parentWorkingSet=workingSet,
            datasetIds=[itemId],
        )
