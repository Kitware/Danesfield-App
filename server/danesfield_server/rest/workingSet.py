#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
###############################################################################

from bson.objectid import ObjectId
from girder.api import access
from girder.api.describe import autoDescribeRoute, Description
from girder.api.rest import Resource
from girder.models.item import Item
from girder.models.folder import Folder
from ..models.workingSet import WorkingSet


class WorkingSetResource(Resource):
    def __init__(self):
        super(WorkingSetResource, self).__init__()

        self.resourceName = "workingSet"
        self.route("GET", (), self.getAll)
        self.route("GET", (":id",), self.get)
        self.route("POST", (), self.create)
        self.route("PUT", (":id",), self.edit)
        self.route("DELETE", (":id",), self.delete)
        self.route(
            "GET",
            (
                ":id",
                "evaluationItems",
            ),
            self.getEvaluationItems,
        )

    @autoDescribeRoute(
        Description("")
        .errorResponse()
        .errorResponse("Read access was denied on the item.", 403)
    )
    @access.user
    def getAll(self, params):
        return list(WorkingSet().find({}))

    @autoDescribeRoute(
        Description("")
        .modelParam("id", model=WorkingSet, destName="workingSet")
        .errorResponse()
        .errorResponse("Read access was denied on the item.", 403)
    )
    @access.user
    def get(self, workingSet, params):
        return workingSet

    @autoDescribeRoute(
        Description("")
        .jsonParam("data", "", requireObject=True, paramType="body")
        .errorResponse()
        .errorResponse("Read access was denied on the item.", 403)
    )
    @access.user
    def create(self, data, params):
        data["datasetIds"] = self.normalizeworkingSetDatasets(data["datasetIds"])
        if data.get("parentWorkingSetId"):
            data["parentWorkingSetId"] = ObjectId(data["parentWorkingSetId"])

        return WorkingSet().save(data)

    @autoDescribeRoute(
        Description("")
        .modelParam("id", model=WorkingSet, destName="workingSet")
        .jsonParam("data", "", requireObject=True, paramType="body")
        .errorResponse()
        .errorResponse("Read access was denied on the item.", 403)
    )
    @access.user
    def edit(self, workingSet, data, params):
        data.pop("_id", None)
        data["datasetIds"] = self.normalizeworkingSetDatasets(data["datasetIds"])
        workingSet.update(data)
        return WorkingSet().save(workingSet)

    @autoDescribeRoute(
        Description("")
        .modelParam("id", model=WorkingSet, destName="workingSet")
        .errorResponse()
        .errorResponse("Read access was denied on the item.", 403)
    )
    @access.user
    def delete(self, workingSet, params):
        childWorkingSets = WorkingSet().find({"parentWorkingSetId": workingSet["_id"]})

        # Remove child workingSets
        for ws in childWorkingSets:
            WorkingSet().remove(ws)

        # Remove workingSet output folder
        output_folder_id = workingSet.get("output_folder_id")
        if output_folder_id:
            output_folder = Folder().findOne({"_id": output_folder_id})
            Folder().remove(output_folder)

        # Remove workingSet
        WorkingSet().remove(workingSet)

        return

    def normalizeworkingSetDatasets(self, datasetIds):
        datasetIdsSet = set(datasetIds)
        for datasetId in datasetIds:
            datasetItem = Item().findOne({"_id": ObjectId(datasetId)})
            # first remove all tar items
            if datasetItem["name"].endswith(".tar"):
                datasetIdsSet.remove(datasetId)
            elif datasetItem["name"].endswith(".NTF"):
                # Try to include coresponding MSI or PAN item
                msiOrPans = list(
                    Item().find(
                        {
                            "$and": [
                                {"_id": {"$ne": ObjectId(datasetId)}},
                                {
                                    "name": {
                                        "$regex": "^"
                                        + datasetItem["name"].split("-")[0]
                                        + ".*.NTF$"
                                    }
                                },
                            ]
                        }
                    )
                )
                if len(msiOrPans) == 1:
                    datasetIdsSet.add(str(msiOrPans[0]["_id"]))

        for datasetId in list(datasetIdsSet):
            datasetItem = Item().findOne({"_id": ObjectId(datasetId)})
            if datasetItem["name"].endswith(".NTF"):
                # Include conresponding TAR items
                tarItem = Item().findOne(
                    {
                        "name": datasetItem["name"].replace(".NTF", ".tar"),
                        "folderId": datasetItem["folderId"],
                    }
                )
                if tarItem:
                    datasetIdsSet.add(str(tarItem["_id"]))

        return list(datasetIdsSet)

    @autoDescribeRoute(
        Description("")
        .modelParam("id", model=WorkingSet, destName="workingSet")
        .errorResponse()
        .errorResponse("Read access was denied on the item.", 403)
    )
    @access.user
    def getEvaluationItems(self, workingSet, params):
        user = self.getCurrentUser()
        return {
            "childrenWorkingSetEvaluationItems": self.getChildrenWorkingSetEvaluationItems(
                user, workingSet
            ),
            "evaluationItems": self.getWorkingSetEvaluationItems(user, workingSet),
        }

    def getChildrenWorkingSetEvaluationItems(self, user, workingSet):
        childrenWorkingSets = list(
            WorkingSet().find({"parentWorkingSetId": workingSet["_id"]})
        )
        if not len(childrenWorkingSets):
            return []
        childrenWorkingSetevaluationItems = []
        for childWorkingSet in childrenWorkingSets:
            childWorkingSetEvaluationItems = self.getWorkingSetEvaluationItems(
                user, childWorkingSet
            )
            for resultItem in list(childWorkingSetEvaluationItems):
                existingSameNameItems = filter(
                    lambda item: item["name"] == resultItem["name"],
                    childrenWorkingSetevaluationItems,
                )
                if existingSameNameItems:
                    childrenWorkingSetevaluationItems.remove(existingSameNameItems[0])
                childrenWorkingSetevaluationItems.append(resultItem)
        return childrenWorkingSetevaluationItems

    def getWorkingSetEvaluationItems(self, user, workingSet):
        datasetItem = Item().findOne({"_id": ObjectId(workingSet["datasetIds"][0])})
        if not datasetItem:
            return []
        stepResultFolder = Folder().findOne({"_id": datasetItem["folderId"]})
        if stepResultFolder["name"] in evaluationMapping:
            regexes = evaluationMapping[stepResultFolder["name"]]
            return list(
                Item().find(
                    {
                        "$and": [
                            {"folderId": stepResultFolder["_id"]},
                            {"$or": [{"name": {"$regex": regex}} for regex in regexes]},
                        ]
                    }
                )
            )
        return []


evaluationMapping = {
    "buildings-to-dsm": ["_CLS.tif$", "_DSM.tif$"],
    "classify-materials": ["_MTL.tif$"],
    "fit-dtm": ["_DTM.tif$"],
    "generate-dsm": ["_DSM.tif$"],
    "segment-by-height": ["_CLS.tif$"],
    "texture-mapping": ["^((?!xxxx[.]obj).)*$"],
}
