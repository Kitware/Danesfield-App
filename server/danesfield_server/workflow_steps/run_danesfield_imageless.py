#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
###############################################################################

from danesfield_server.workflow import DanesfieldWorkflowException
from typing import Dict

import tempfile
from docker.types import DeviceRequest
from girder.models.collection import Collection
from girder.models.folder import Folder
from girder.models.user import User
from girder_worker.docker.tasks import docker_run
from girder_worker.docker.transforms.girder import (
    GirderUploadVolumePathToFolder,
)
from girder_worker.docker.transforms import BindMountVolume, VolumePath

from danesfield_server.algorithms.common import (
    addJobInfo,
    createDockerRunArguments,
    createGirderClient,
)

from ..constants import DanesfieldStep, DockerImage
from ..workflow_step import DanesfieldWorkflowStep
from ..workflow_utilities import getWorkingSet
from ..models.workingSet import WorkingSet


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

        core3dCollection = Collection().createCollection(
            name="core3d",
            creator=User().getAdmins().next(),
            description="",
            public=True,
            reuseExisting=True,
        )

        modelsFolder = Folder().findOne(
            {
                "parentId": core3dCollection["_id"],
                "name": "models",
            }
        )
        if modelsFolder is None:
            raise DanesfieldWorkflowException(
                "Models folder has not been created and populated"
            )

        # Download models folder
        models_folder = tempfile.mkdtemp()
        modelsFolderVolume = BindMountVolume(models_folder, models_folder)
        gc.downloadFolderRecursive(modelsFolder["_id"], models_folder)

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
                # May need to update below
                + f"rpc_dir = {tempfile.mkdtemp()}\n"
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
            roof_section = (
                "[roof]\n"
                + f"model_dir = {models_folder}/Columbia Geon Segmentation Model\n"
                + "model_prefix = dayton_geon"
            )
            in_config_file.write(f"{roof_section}\n")

        # Ensure folder exists
        existing_folder_id = baseWorkingSet.get("output_folder_id")
        if existing_folder_id is None:
            output_folder = Folder().createFolder(
                parent=core3dCollection,
                parentType="collection",
                name=f"(Imageless) {baseWorkingSet['name']}",
                reuseExisting=True,
            )
            existing_folder_id = output_folder["_id"]
            baseWorkingSet["output_folder_id"] = output_folder["_id"]
            WorkingSet().save(baseWorkingSet)

        # Pull down contents of existing output folder
        gc.downloadFolderRecursive(existing_folder_id, outputDir)

        containerArgs = [
            # "touch",
            # f"{outputDir}/test.txt",
            "python",
            "/danesfield/tools/run_danesfield_imageless.py",
            config_file_path,
        ]

        # Ensure result is uploaded to output folder
        resultHooks = [
            GirderUploadVolumePathToFolder(
                VolumePath(".", volume=outputDirVolume),
                existing_folder_id,
                delete_file=True,
            )
        ]

        asyncResult = docker_run.delay(
            device_requests=[DeviceRequest(count=-1, capabilities=[["gpu"]])],
            shm_size="8G",
            volumes=[
                pointCloudFileVolume,
                configFileVolume,
                outputDirVolume,
                modelsFolderVolume,
                #
                # Test mount
                BindMountVolume(
                    "/home/local/KHQ/jacob.nesbitt/Danesfield-Imageless-Fork/tools",
                    "/danesfield/tools",
                ),
            ],
            **createDockerRunArguments(
                # image=DockerImage.DANESFIELD,
                image="kitware/danesfield:latest",
                containerArgs=containerArgs,
                jobTitle=f"Run imageless workflow on [{baseWorkingSet['name']}]",
                jobType=self.name,
                user=jobInfo.requestInfo.user,
                resultHooks=resultHooks,
            ),
        )

        # Add info for job event listeners
        job = asyncResult.job
        job = addJobInfo(job, jobId=jobInfo.jobId, stepName=self.name)

        return job
