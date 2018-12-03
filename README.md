# Danesfield App

The Danesfield App is a web application for running the [Danesfield](https://github.com/Kitware/Danesfield) algorithms and visualizing results.  Danesfield addresses the algorithmic challenges of the IARPA CORE3D program by reconstructing semantically meaningful 3D models of buildings and other man-made structures from satellite imagery.

## Video demo
<kbd><img src="https://user-images.githubusercontent.com/3123478/49317901-5b759500-f4c4-11e8-9f65-936b718e5f65.gif" /></kbd>

## Screenshots
<kbd><img src="screenshot_1.png" /></kbd>

<kbd><img src="screenshot_2.png" /></kbd>

<kbd><img src="screenshot_3.png" /></kbd>

# Server

## Requirements

This application is built on top of the Girder data management platform.

- [Girder](https://github.com/girder/girder)
- [Girder Worker](https://github.com/girder/girder_worker) at revision [31c28c6](https://github.com/girder/girder_worker/commit/31c28c6db32f56e0a6528cbbc8e38c3000d715e5) or later
- [Girder Geospatial](https://github.com/OpenGeoscience/girder_geospatial)
- [Docker](https://www.docker.com/)

## Setup

### On Girder host

Install the Girder plugin by running:
```bash
girder-install plugin /path/to/danesfield-app/danesfield-server
```

### On Girder Worker host

Ensure that the following Docker images are available:
- `gitlab.kitware.com:4567/core3d/danesfield-app/danesfield`
- `gitlab.kitware.com:4567/core3d/danesfield-app/p3d_gw`

These images may be pulled from the [container registry](https://gitlab.kitware.com/core3d/danesfield-app/container_registry).

Ensure that the [GTOPO 30 data](https://data.kitware.com/#folder/5aa993db8d777f068578d08c) is
available in `/mnt/GTOPO30`. This data is a requirement of P3D.

#### Building the Docker images

Currently, these Docker images are not automatically built. Follow the steps below to build them when necessary.

To build `gitlab.kitware.com:4567/core3d/danesfield-app/danesfield`:
- Run `docker build -t gitlab.kitware.com:4567/core3d/danesfield-app/danesfield .` in the `danesfield` repository root.

To build `gitlab.kitware.com:4567/core3d/danesfield-app/p3d_gw`:
- Follow the linked instructions to build the [p3d Docker image](https://data.kitware.com/#collection/59c1963d8d777f7d33e9d4eb/folder/5aa933de8d777f068578c303).
- Run `docker build -t  gitlab.kitware.com:4567/core3d/danesfield-app/p3d_gw .` in [support/docker/p3d_gw](./support/docker/p3d_gw).

To archive an image for transfer to another system, run `docker save IMAGE_NAME | gzip > image.gz`.

To load an archived image, run `gzip -d -c image.gz | docker load`.

## Configuration



### UNet Semantic Segmentation

- Upload the configuration and model files referenced in the [tool documentation](
  https://github.com/Kitware/Danesfield/tree/master/tools#unet-semantic-segmentation).
- Set the `danesfield.unet_semantic_segmentation_config_file_id` and
  `danesfield.unet_semantic_segmentation_model_file_id` settings to the IDs of
  those files.

### Building Segmentation

- Upload the model files referenced in the [tool documentation](
https://github.com/Kitware/Danesfield/tree/master/tools#columbia-building-segmentation)
to a Girder folder.
- Set the `danesfield.building_segmentation_model_folder_id` setting to the ID of that folder.

### Material Classification

- Upload the model file referenced in the [tool documentation](
https://github.com/Kitware/Danesfield/tree/master/tools#material-classification)
to Girder.
- Set the `danesfield.material_classifier_model_file_id` setting to the ID of that file.

### Roof Geon Extraction

- Upload the model files referenced in the [tool documentation](
  https://github.com/Kitware/Danesfield/tree/master/tools#roof-geon-extraction)
  into a folder on Girder.
- Set the `danesfield.roof_segmentation_model_folder_id` setting to the ID of that folder.

### Run Metrics

- Upload the ground truth data files referenced in the [tool
  documentation](
  https://github.com/Kitware/Danesfield/tree/master/tools#run-metrics)
  into a folder on Girder.
- Set the `danesfield.reference_data_folder_id` setting to the ID of that folder.

# Client Setup
See [here](client/README.md)
