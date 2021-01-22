#!/bin/sh

exec /tini -v -- girder serve --host 0.0.0.0
