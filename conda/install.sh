#!/bin/bash

# Exit if any commands fail
set -e

# Initialize conda
source $(conda info --base)/etc/profile.d/conda.sh

# Env
conda env create -f conda/conda_environment.yml
conda activate danesfield
mkdir -p $CONDA_PREFIX/var/lib/mongodb

# girder
pip install -e server/
pip install -U pip setuptools

# client
git submodule update --init --recursive
npm install -g yarn
yarn --cwd client/ --frozen-lockfile
yarn --cwd client/ build

# Run girder build
girder build

# Copy static files
cp -r client/dist $CONDA_PREFIX/share/girder/static/core3d
