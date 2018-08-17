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

import six

from girder.exceptions import ValidationException
from girder.utility import setting_utilities


class PluginSettings(object):
    MATERIAL_CLASSIFIER_MODEL_FILE_ID = 'danesfield.material_classifier_model_file_id'


@setting_utilities.validator(PluginSettings.MATERIAL_CLASSIFIER_MODEL_FILE_ID)
def _validateMaterialClassifierModelFileId(doc):
    if not isinstance(doc['value'], six.string_types):
        raise ValidationException('Material classifier model file ID must be a string.')


@setting_utilities.default(PluginSettings.MATERIAL_CLASSIFIER_MODEL_FILE_ID)
def _defaultMaterialClassifierModelFileId():
    return ''
