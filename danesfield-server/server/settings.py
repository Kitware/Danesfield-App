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
    MATERIAL_CLASSIFIER_STANDARD_MODEL_FILE_ID = 'danesfield.material_classifier_standard_model_file_id'
    MATERIAL_CLASSIFIER_D1_MODEL_FILE_ID = 'danesfield.material_classifier_D1_model_file_id'
    MATERIAL_CLASSIFIER_D2_MODEL_FILE_ID = 'danesfield.material_classifier_D2_model_file_id'
    MATERIAL_CLASSIFIER_D3_MODEL_FILE_ID = 'danesfield.material_classifier_D3_model_file_id'
    MATERIAL_CLASSIFIER_D4_MODEL_FILE_ID = 'danesfield.material_classifier_D4_model_file_id'
    UNET_SEMANTIC_SEGMENTATION_CONFIG_FILE_ID = \
        'danesfield.unet_semantic_segmentation_config_file_id'
    UNET_SEMANTIC_SEGMENTATION_MODEL_FILE_ID = 'danesfield.unet_semantic_segmentation_model_file_id'
    ROOF_SEGMENTATION_MODEL_FOLDER_ID = 'danesfield.roof_segmentation_model_folder_id'
    SEGMENT_BY_HEIGHT_SHAPEFILES_FOLDER_ID = 'danesfield.segment_by_height_shapefiles_folder_id'
    REFERENCE_DATA_FOLDER_ID = 'danesfield.reference_data_folder_id'


@setting_utilities.validator(PluginSettings.BUILDING_SEGMENTATION_MODEL_FOLDER_ID)
def _validateBuildingSegmentationModelFolderId(doc):
    if not isinstance(doc['value'], six.string_types):
        raise ValidationException('Building segmentation model folder ID must be a string.')


@setting_utilities.default(PluginSettings.BUILDING_SEGMENTATION_MODEL_FOLDER_ID)
def _defaultBuildingSegmentationModelFolderId():
    return ''


@setting_utilities.validator(PluginSettings.MATERIAL_CLASSIFIER_STANDARD_MODEL_FILE_ID)
def _validateMaterialClassifierStandardModelFileId(doc):
    if not isinstance(doc['value'], six.string_types):
        raise ValidationException('Material classifier standard model file ID must be a string.')


@setting_utilities.default(PluginSettings.MATERIAL_CLASSIFIER_STANDARD_MODEL_FILE_ID)
def _defaultMaterialClassifierStandardModelFileId():
    return ''


@setting_utilities.validator(PluginSettings.MATERIAL_CLASSIFIER_D1_MODEL_FILE_ID)
def _validateMaterialClassifierD1ModelFileId(doc):
    if not isinstance(doc['value'], six.string_types):
        raise ValidationException('Material classifier D1 model file ID must be a string.')


@setting_utilities.default(PluginSettings.MATERIAL_CLASSIFIER_D1_MODEL_FILE_ID)
def _defaultMaterialClassifierD1ModelFileId():
    return ''


@setting_utilities.validator(PluginSettings.MATERIAL_CLASSIFIER_D2_MODEL_FILE_ID)
def _validateMaterialClassifierD2ModelFileId(doc):
    if not isinstance(doc['value'], six.string_types):
        raise ValidationException('Material classifier D2 model file ID must be a string.')


@setting_utilities.default(PluginSettings.MATERIAL_CLASSIFIER_D2_MODEL_FILE_ID)
def _defaultMaterialClassifierD2ModelFileId():
    return ''


@setting_utilities.validator(PluginSettings.MATERIAL_CLASSIFIER_D3_MODEL_FILE_ID)
def _validateMaterialClassifierD3ModelFileId(doc):
    if not isinstance(doc['value'], six.string_types):
        raise ValidationException('Material classifier D3 model file ID must be a string.')


@setting_utilities.default(PluginSettings.MATERIAL_CLASSIFIER_D3_MODEL_FILE_ID)
def _defaultMaterialClassifierD3ModelFileId():
    return ''


@setting_utilities.validator(PluginSettings.MATERIAL_CLASSIFIER_D4_MODEL_FILE_ID)
def _validateMaterialClassifierD4ModelFileId(doc):
    if not isinstance(doc['value'], six.string_types):
        raise ValidationException('Material classifier D4 model file ID must be a string.')


@setting_utilities.default(PluginSettings.MATERIAL_CLASSIFIER_D4_MODEL_FILE_ID)
def _defaultMaterialClassifierD4ModelFileId():
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


@setting_utilities.validator(PluginSettings.SEGMENT_BY_HEIGHT_SHAPEFILES_FOLDER_ID)
def _validateSegmentByHeightShapefilesFolderId(doc):
    if not isinstance(doc['value'], six.string_types):
        raise ValidationException('Building segmentation model folder ID must be a string.')


@setting_utilities.default(PluginSettings.SEGMENT_BY_HEIGHT_SHAPEFILES_FOLDER_ID)
def _defaultSegmentByHeightShapefilesFolderId():
    return ''


@setting_utilities.validator(PluginSettings.REFERENCE_DATA_FOLDER_ID)
def _validateReferenceDataFolderId(doc):
    if not isinstance(doc['value'], six.string_types):
        raise ValidationException('Reference data folder ID must be a string.')


@setting_utilities.default(PluginSettings.REFERENCE_DATA_FOLDER_ID)
def _defaultReferenceDataFolderId():
    return ''
