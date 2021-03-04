#!/bin/sh

cd /home/core3d
pip install -e .

python3 /home/provision/init_girder.py
exec /tini -v -- girder serve --dev --host 0.0.0.0
