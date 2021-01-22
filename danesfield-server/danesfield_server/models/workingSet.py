###############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
###############################################################################

from bson.objectid import ObjectId

from girder.exceptions import ValidationException
from girder.models.model_base import Model


class WorkingSet(Model):
    def initialize(self):
        self.name = "workingSet"
        self.ensureIndex("name")
        self.ensureIndex("parentWorkingSetId")

    def validate(self, model):
        # Name must not be empty
        if not model["name"]:
            raise ValidationException("Name must not be empty.", "name")

        # Dataset IDs must be a list
        if not isinstance(model["datasetIds"], list):
            raise ValidationException("Dataset IDs must be a list.", "datasetIds")

        return model

    def createWorkingSet(
        self, name, parentWorkingSet=None, datasetIds=[], filterId=None
    ):
        """
        Create a new working set.
        """
        doc = {
            "name": name,
            "parentWorkingSetId": parentWorkingSet["_id"]
            if parentWorkingSet is not None
            else None,
            "datasetIds": [ObjectId(datasetId) for datasetId in datasetIds],
        }

        if filterId:
            doc["filterId"] = filterId

        return self.save(doc)
