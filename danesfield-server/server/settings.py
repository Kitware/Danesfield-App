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
    BUILDING_SEGMENTATION_MODEL_FOLDER_ID = 'danesfield.building_segmentation_model_folder_id'
    MATERIAL_CLASSIFIER_MODEL_FILE_ID = 'danesfield.material_classifier_model_file_id'
    UNET_SEMANTIC_SEGMENTATION_CONFIG_FILE_ID = \
        'danesfield.unet_semantic_segmentation_config_file_id'
    UNET_SEMANTIC_SEGMENTATION_MODEL_FILE_ID = 'danesfield.unet_semantic_segmentation_model_file_id'
    ROOF_SEGMENTATION_MODEL_FOLDER_ID = 'danesfield.roof_segmentation_model_folder_id'


@setting_utilities.validator(PluginSettings.BUILDING_SEGMENTATION_MODEL_FOLDER_ID)
def _validateBuildingSegmentationModelFolderId(doc):
    if not isinstance(doc['value'], six.string_types):
        raise ValidationException('Building segmentation model folder ID must be a string.')


@setting_utilities.default(PluginSettings.BUILDING_SEGMENTATION_MODEL_FOLDER_ID)
def _defaultBuildingSegmentationModelFolderId():
    return ''


@setting_utilities.validator(PluginSettings.MATERIAL_CLASSIFIER_MODEL_FILE_ID)
def _validateMaterialClassifierModelFileId(doc):
    if not isinstance(doc['value'], six.string_types):
        raise ValidationException('Material classifier model file ID must be a string.')


@setting_utilities.default(PluginSettings.MATERIAL_CLASSIFIER_MODEL_FILE_ID)
def _defaultMaterialClassifierModelFileId():
    return ''


@setting_utilities.validator(PluginSettings.ROOF_SEGMENTATION_MODEL_FOLDER_ID)
def _validateRoofSegmentationModelFolderId(doc):
    if not isinstance(doc['value'], six.string_types):
        raise ValidationException('Roof segmentation model folder ID must be a string.')


@setting_utilities.default(PluginSettings.ROOF_SEGMENTATION_MODEL_FOLDER_ID)
def _defaultRoofSegmentationModelFolderId():
    return ''


@setting_utilities.validator(PluginSettings.UNET_SEMANTIC_SEGMENTATION_CONFIG_FILE_ID)
def _validateUNetSemanticSegmentationConfigFileId(doc):
    if not isinstance(doc['value'], six.string_types):
        raise ValidationException(
            'UNet semantic segmentation configuration file ID must be a string.')


@setting_utilities.default(PluginSettings.UNET_SEMANTIC_SEGMENTATION_CONFIG_FILE_ID)
def _defaultUNetSemanticSegmentationConfigFileId():
    return ''


@setting_utilities.validator(PluginSettings.UNET_SEMANTIC_SEGMENTATION_MODEL_FILE_ID)
def _validateUNetSemanticSegmentationModelFileId(doc):
    if not isinstance(doc['value'], six.string_types):
        raise ValidationException('UNet semantic segmentation model file ID must be a string.')


@setting_utilities.default(PluginSettings.UNET_SEMANTIC_SEGMENTATION_MODEL_FILE_ID)
def _defaultUNetSemanticSegmentationModelFileId():
    return ''
