#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
###############################################################################


from . import loader
from girder.plugin import GirderPlugin


class DanesfieldPlugin(GirderPlugin):
    def load(self, info):
        loader.load(info)
