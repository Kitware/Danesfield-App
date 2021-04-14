#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
###############################################################################

import itertools
import shutil
from typing import List, Union
import docker

import os
import json
import tempfile
import utm
from pathlib import Path

from docker.types import DeviceRequest
from girder_worker.docker.tasks import docker_run

# from girder_worker.docker.transforms import Transform
from girder_worker_utils.transforms.girder_io import ResultTransform
from girder_worker.docker.transforms import BindMountVolume
from girder_worker.docker.transforms.girder import (
    GirderUploadVolumePathToFolder,
)

from .common import (
    addJobInfo,
    createDockerRunArguments,
    createGirderClient,
    createUploadMetadata,
)
from ..constants import DockerImage


class RemoveTemporaryPathsTransform(ResultTransform):
    """Remove specified files/folders as a result hook."""

    def __init__(self, paths: List[Union[Path, str]]) -> None:
        self.paths = paths

    def exception(self):
        pass

    def transform(self, *args, **kwargs):
        for pathname in self.paths:
            path = Path(pathname)
            if not path.exists:
                continue

            if path.is_file():
                os.remove(path)

            if path.is_dir():
                shutil.rmtree(path)


class ResultRunDockerCommand(ResultTransform):
    """Call `docker run` as a result hook."""

    def __init__(self, *args, **kwargs) -> None:
        self.args = args
        self.kwargs = kwargs

    def exception(self):
        pass

    def transform(self, *args, **kwargs):
        client = docker.from_env()
        client.containers.run(*self.args, **self.kwargs)


def generatePointCloud(
    initWorkingSetName,
    stepName,
    requestInfo,
    jobId,
    outputFolder,
    filePairs,
    aoiBBox,
):
    """
    Run a Girder Worker job to generate a 3D point cloud from 2D images.

    Requirements:
    - Danesfield Docker image is available on host

    :param initWorkingSetName: The name of the top-level working set.
    :type initWorkingSetName: str
    :param stepName: The name of the step.
    :type stepName: str (DanesfieldStep)
    :param requestInfo: HTTP request and authorization info.
    :type requestInfo: RequestInfo
    :param jobId: Job ID.
    :type jobId: str
    :param outputFolder: Output folder document.
    :type outputFolder: dict
    :param filePairs: List of tuples of the form (imageFile, tarFile)
    :type filePairs: list[tuple[girder_file, girder_file]]
    :param aoiBBox: The AOI bounding box
    :type aoiBBox: list[float]
    :returns: Job document.
    """
    gc = createGirderClient(requestInfo)

    outputDir = tempfile.mkdtemp()
    outputDirBindMountVolume = BindMountVolume(
        host_path=outputDir, container_path=outputDir
    )

    datasetDir = tempfile.mkdtemp()
    datasetDirPath = Path(datasetDir)

    # Download images and tars to dir
    for pair in filePairs:
        for file in pair:
            filepath = datasetDirPath / file["name"]
            gc.downloadFile(str(file["_id"]), str(filepath))

    # Calculate variables from bbox
    minX, minY, maxX, maxY = aoiBBox
    hemisphere = "N" if maxY > 0 else "S"
    ul_easting, ul_northing, zone_number, zone_letter = utm.from_latlon(maxY, minX)
    br_easting, br_northing, _, _ = utm.from_latlon(minY, maxX)
    width = abs(ul_easting - br_easting)
    height = abs(ul_northing - br_northing)
    utm_zone = f"{zone_number}{zone_letter}"

    # Create config dict
    config_dict = {
        "dataset_dir": datasetDir,
        "work_dir": outputDir,
        "bounding_box": {
            "zone_number": zone_number,
            "hemisphere": hemisphere,
            "ul_easting": ul_easting,
            "ul_northing": ul_northing,
            "width": width,
            "height": height,
        },
        "steps_to_run": {
            "clean_data": True,
            "crop_image": True,
            "derive_approx": True,
            "choose_subset": True,
            "colmap_sfm_perspective": True,
            "inspect_sfm_perspective": False,
            "reparam_depth": True,
            "colmap_mvs": True,
            "aggregate_2p5d": True,
            "aggregate_3d": True,
        },
        # TODO: Example data, needs to be parameterized
        "alt_min": -30.0,
        "alt_max": 120.0,
    }

    # Specify output filename
    point_cloud_output_filename = f"{outputDir}/point_cloud.las"

    # Create and write to config file
    config_file_path = tempfile.mkstemp(suffix=".json")[1]
    with open(config_file_path, "w") as config_file_in:
        config_file_in.write(json.dumps(config_dict, indent=2))

    # Docker volumes
    volumes = [
        BindMountVolume(
            host_path=config_file_path,
            container_path=config_file_path,
            mode="ro",
        ),
        BindMountVolume(
            host_path=datasetDir,
            container_path=datasetDir,
            mode="ro",
        ),
        outputDirBindMountVolume,
    ]

    # Docker container arguments
    # TODO: Consider a solution where args are written to a file, in
    # case of very long command lines

    device_requests = [DeviceRequest(count=-1, capabilities=[["gpu"]])]
    containerArgs = list(
        itertools.chain(
            [
                "python",
                "/danesfield/tools/generate_point_cloud.py",
                "--config_file",
                config_file_path,
                "--work_dir",
                outputDir,
                "--point_cloud",
                point_cloud_output_filename,
                "--utm",
                utm_zone,
            ],
        )
    )

    resultHooks = [
        # - Fix output folder permissions
        ResultRunDockerCommand(
            DockerImage.DANESFIELD,
            command=["chown", "-R", f"{os.getuid()}:{os.getgid()}", outputDir],
            volumes=outputDirBindMountVolume._repr_json_(),
        ),
        # - Provide upload metadata & upload output files to output folder
        GirderUploadVolumePathToFolder(
            outputDir,
            outputFolder["_id"],
            upload_kwargs=createUploadMetadata(jobId, stepName),
            gc=gc,
        ),
        # - Remove temporary files/folders
        RemoveTemporaryPathsTransform([outputDir, datasetDir, config_file_path]),
    ]

    asyncResult = docker_run.delay(
        volumes=volumes,
        device_requests=device_requests,
        **createDockerRunArguments(
            image=DockerImage.DANESFIELD,
            containerArgs=containerArgs,
            jobTitle="[%s] Generate point cloud" % initWorkingSetName,
            jobType=stepName,
            user=requestInfo.user,
            resultHooks=resultHooks,
        ),
    )

    # Add info for job event listeners
    job = asyncResult.job
    job = addJobInfo(job, jobId=jobId, stepName=stepName)

    return job
