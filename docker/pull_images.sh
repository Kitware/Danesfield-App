#!/bin/sh

# Login
docker login https://gitlab.kitware.com:4567/v2/core3d/danesfield-app 

# Pull and Tag Danesfield Image
docker pull kitware/danesfield
docker tag kitware/danesfield:latest gitlab.kitware.com:4567/core3d/danesfield-app/danesfield:latest

# Pull P3D Image
docker pull gitlab.kitware.com:4567/core3d/danesfield-app/p3d_gw

