#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
###############################################################################

from typing import Dict
from girder_worker.docker.tasks import docker_run
from girder_worker.docker.transforms.girder import GirderUploadVolumePathToFolder
from danesfield_server.algorithms.common import (
    addJobInfo,
    createDockerRunArguments,
    createGirderClient,
)
import tempfile

from girder_worker.docker.transforms import BindMountVolume
from ..constants import DanesfieldStep, DockerImage
from ..workflow_step import DanesfieldWorkflowStep
from ..workflow_utilities import getWorkingSet


class RunDanesfieldImageless(DanesfieldWorkflowStep):
    """
    Step that generates a point cloud.

    Supports the following options:
    - aoiBBox (required)
    """

    def __init__(self):
        super(RunDanesfieldImageless, self).__init__("Imageless")
        self.addDependency(DanesfieldStep.GENERATE_POINT_CLOUD)

    def run(self, jobInfo, outputFolder):
        gc = createGirderClient(jobInfo.requestInfo)
        baseWorkingSet: Dict = getWorkingSet(DanesfieldStep.INIT, jobInfo)

        # Get point cloud working set
        pointCloudWorkingSet: Dict = getWorkingSet(
            DanesfieldStep.GENERATE_POINT_CLOUD, jobInfo
        )

        # Get single file, there will only be one
        point_cloud_path = tempfile.mktemp(suffix=".las")
        pointCloudFile = self.getFiles(pointCloudWorkingSet)[0]
        gc.downloadFile(str(pointCloudFile["_id"]), point_cloud_path)
        pointCloudFileVolume = BindMountVolume(point_cloud_path, point_cloud_path)

        # Create output dir
        outputDir = tempfile.mkdtemp()
        outputDirVolume = BindMountVolume(host_path=outputDir, container_path=outputDir)

        # Create config file
        config_file, config_file_path = tempfile.mkstemp(suffix=".ini")
        configFileVolume = BindMountVolume(config_file_path, config_file_path)
        with open(config_file, "w") as in_config_file:
            # Configure paths
            paths_section = (
                "[paths]\n"
                + f"p3d_fpath = {point_cloud_path}\n"
                + f"work_dir = {outputDir}\n"
                + "rpc_dir = /tmp/asdasdsdjshdjshdjsds\n"
            )
            in_config_file.write(f"{paths_section}\n")

            # Set name prefix for output files
            aoi_section = (
                "[aoi]\n" + f"name = {baseWorkingSet['name'].replace(' ', '_')}"
            )
            in_config_file.write(f"{aoi_section}\n")

            # Ground sample distancy of output imagery in meters per pixel
            # Default is 0.25
            params_section = "[params]\n" + "gsd = 0.25\n"
            in_config_file.write(f"{params_section}\n")

            # Parameters for the roof geon extraction step
            # TODO: Download models into MODEL_DIR and use in below line
            roof_section = (
                "[roof]\n" + "model_dir = MODEL_DIR\n" + "model_prefix = dayton_geon"
            )
            in_config_file.write(f"{roof_section}\n")

        # Pull down existing output folder, if it exists
        existing_folder_id = baseWorkingSet.get("output_folder_id")
        if existing_folder_id is not None:
            gc.downloadFolderRecursive(existing_folder_id, outputDir)

        containerArgs = [
            "python",
            "/danesfield/tools/run_danesfield_imageless.py",
            config_file_path,
        ]

        # TODO: Add GirderUploadVolumePathToFolder transform to resultHooks
        # resultHooks=[GirderUploadVolumePathToFolder(outputDirVolume, )],

        asyncResult = docker_run.delay(
            runtime="nvidia",
            volumes=[
                pointCloudFileVolume,
                configFileVolume,
                outputDirVolume,
                # Test mount
                BindMountVolume(
                    "/home/local/KHQ/jacob.nesbitt/Danesfield-Imageless-Fork/tools",
                    "/danesfield/tools",
                ),
            ],
            **createDockerRunArguments(
                image=DockerImage.DANESFIELD,
                containerArgs=containerArgs,
                jobTitle=f"Run imageless workflow on [{baseWorkingSet['name']}]",
                jobType=self.name,
                user=jobInfo.requestInfo.user,
                # resultHooks=resultHooks,
            ),
        )

        # Add info for job event listeners
        job = asyncResult.job
        job = addJobInfo(job, jobId=jobInfo.jobId, stepName=self.name)

        return job
