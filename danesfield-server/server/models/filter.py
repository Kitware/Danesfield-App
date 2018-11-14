###############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
###############################################################################

from girder.models.model_base import Model


class Filter(Model):

    def initialize(self):
        self.name = 'filter'

    def validate(self, model):
        return model
