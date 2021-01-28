#!/bin/sh

# Pull and Tag Danesfield Image
docker pull kitware/danesfield
docker tag kitware/danesfield:latest gitlab.kitware.com:4567/core3d/danesfield-app/danesfield:latest

# Pull P3D Image
docker pull gitlab.kitware.com:4567/core3d/danesfield-app/p3d_gw

