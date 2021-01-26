#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
###############################################################################

import six

from girder.exceptions import ValidationException
from girder.utility import setting_utilities


class PluginSettings:
    BUILDING_SEGMENTATION_MODEL_FOLDER_ID = (
        "danesfield.building_segmentation_model_folder_id"
    )
    MATERIAL_CLASSIFIER_MODEL_FOLDER_ID = (
        "danesfield.material_classifier_model_folder_id"
    )
    UNET_SEMANTIC_SEGMENTATION_CONFIG_FILE_ID = (
        "danesfield.unet_semantic_segmentation_config_file_id"
    )
    UNET_SEMANTIC_SEGMENTATION_MODEL_FILE_ID = (
        "danesfield.unet_semantic_segmentation_model_file_id"
    )
    ROOF_SEGMENTATION_MODEL_FOLDER_ID = "danesfield.roof_segmentation_model_folder_id"
    SEGMENT_BY_HEIGHT_SHAPEFILES_FOLDER_ID = (
        "danesfield.segment_by_height_shapefiles_folder_id"
    )
    REFERENCE_DATA_FOLDER_ID = "danesfield.reference_data_folder_id"


@setting_utilities.validator(PluginSettings.BUILDING_SEGMENTATION_MODEL_FOLDER_ID)
def _validateBuildingSegmentationModelFolderId(doc):
    if not isinstance(doc["value"], six.string_types):
        raise ValidationException(
            "Building segmentation model folder ID must be a string."
        )


@setting_utilities.default(PluginSettings.BUILDING_SEGMENTATION_MODEL_FOLDER_ID)
def _defaultBuildingSegmentationModelFolderId():
    return ""


@setting_utilities.validator(PluginSettings.MATERIAL_CLASSIFIER_MODEL_FOLDER_ID)
def _validateMaterialClassifierModelFolderId(doc):
    if not isinstance(doc["value"], six.string_types):
        raise ValidationException(
            "Material classifier model folder ID must be a string."
        )


@setting_utilities.default(PluginSettings.MATERIAL_CLASSIFIER_MODEL_FOLDER_ID)
def _defaultMaterialClassifierModelFolderId():
    return ""


@setting_utilities.validator(PluginSettings.ROOF_SEGMENTATION_MODEL_FOLDER_ID)
def _validateRoofSegmentationModelFolderId(doc):
    if not isinstance(doc["value"], six.string_types):
        raise ValidationException("Roof segmentation model folder ID must be a string.")


@setting_utilities.default(PluginSettings.ROOF_SEGMENTATION_MODEL_FOLDER_ID)
def _defaultRoofSegmentationModelFolderId():
    return ""


@setting_utilities.validator(PluginSettings.UNET_SEMANTIC_SEGMENTATION_CONFIG_FILE_ID)
def _validateUNetSemanticSegmentationConfigFileId(doc):
    if not isinstance(doc["value"], six.string_types):
        raise ValidationException(
            "UNet semantic segmentation configuration " "file ID must be a string."
        )


@setting_utilities.default(PluginSettings.UNET_SEMANTIC_SEGMENTATION_CONFIG_FILE_ID)
def _defaultUNetSemanticSegmentationConfigFileId():
    return ""


@setting_utilities.validator(PluginSettings.UNET_SEMANTIC_SEGMENTATION_MODEL_FILE_ID)
def _validateUNetSemanticSegmentationModelFileId(doc):
    if not isinstance(doc["value"], six.string_types):
        raise ValidationException(
            "UNet semantic segmentation model file ID must be a string."
        )


@setting_utilities.default(PluginSettings.UNET_SEMANTIC_SEGMENTATION_MODEL_FILE_ID)
def _defaultUNetSemanticSegmentationModelFileId():
    return ""


@setting_utilities.validator(PluginSettings.SEGMENT_BY_HEIGHT_SHAPEFILES_FOLDER_ID)
def _validateSegmentByHeightShapefilesFolderId(doc):
    if not isinstance(doc["value"], six.string_types):
        raise ValidationException(
            "Building segmentation model folder ID must be a string."
        )


@setting_utilities.default(PluginSettings.SEGMENT_BY_HEIGHT_SHAPEFILES_FOLDER_ID)
def _defaultSegmentByHeightShapefilesFolderId():
    return ""


@setting_utilities.validator(PluginSettings.REFERENCE_DATA_FOLDER_ID)
def _validateReferenceDataFolderId(doc):
    if not isinstance(doc["value"], six.string_types):
        raise ValidationException("Reference data folder ID must be a string.")


@setting_utilities.default(PluginSettings.REFERENCE_DATA_FOLDER_ID)
def _defaultReferenceDataFolderId():
    return ""
