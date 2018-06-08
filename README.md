# Danesfield App

Application to run Danesfield algorithms.

# Server

## Requirements

- [Girder](https://github.com/girder/girder)
- [Girder Worker](https://github.com/girder/girder_worker) at revision [ad3e384](https://github.com/girder/girder_worker/commit/ad3e384f4894b8fb747b3bab87e39376e3701049) or later
- [Docker](https://www.docker.com/)

## Setup

### On Girder host

Install the Girder plugin by running:
```bash
girder-install plugin /path/to/danesfield-app/danesfield-server
```

### On Girder Worker host

Ensure `core3d/danesfield` Docker image is available by either:
- Building it with `docker build -t core3d/danesfield .` in the `danesfield` repository root.
- Obtain an archive of the image created by `docker save core3d/danesfield | gzip > danesfield.tar.gz`
  and load it with `gzip -d -c danesfield.tar.gz | docker load`.

Ensure `p3d_gw` Docker image is available by:
- Building the [p3d Docker image](https://data.kitware.com/#collection/59c1963d8d777f7d33e9d4eb/folder/5aa933de8d777f068578c303).
- Building the [p3d_gw Docker image](./support/docker/p3d_gw/Dockerfile).
- Alternatively, obtain an archive of the `p3d_gw` image and load it using `docker load`.

Ensure that the [GTOPO 30 data](https://data.kitware.com/#folder/5aa993db8d777f068578d08c) is
available in `/mnt/GTOPO30`. This data is a requirement of P3D.
