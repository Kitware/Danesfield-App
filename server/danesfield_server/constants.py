#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
###############################################################################


class DanesfieldJobKey:
    """
    Keys for metadata attached to Danesfield jobs and related objects.
    """

    ID = "danesfieldJobId"
    STEP_NAME = "danesfieldJobStep"
    WORKINGSETID = "danesfieldWorkingSetId"


class DanesfieldStep:
    """
    Names to identify steps in the Danesfield workflow.
    """

    INIT = "init"
    FIT_DTM = "fit-dtm"
    SELECT_BEST = "select-best"
    GENERATE_DSM = "generate-dsm"
    GENERATE_POINT_CLOUD = "generate-point-cloud"
    MSI_TO_RGB = "msi-to-rgb"
    ORTHORECTIFY = "orthorectify"
    PANSHARPEN = "pansharpen"
    COMPUTE_NDVI = "compute-ndvi"
    SEGMENT_BY_HEIGHT = "segment-by-height"
    UNET_SEMANTIC_SEGMENTATION = "unet-semantic-segmentation"
    BUILDING_SEGMENTATION = "building-segmentation"
    CLASSIFY_MATERIALS = "classify-materials"
    ROOF_GEON_EXTRACTION = "roof-geon-extraction"
    BUILDINGS_TO_DSM = "buildings-to-dsm"
    GET_ROAD_VECTOR = "get-road-vector"
    CROP_AND_PANSHARPEN = "crop-and-pansharpen"
    TEXTURE_MAPPING = "texture-mapping"
    RUN_METRICS = "run-metrics"


class DockerImage:
    """
    Names of Docker images to run Danesfield algorithms.
    """

    DANESFIELD = "kitware/danesfield"
