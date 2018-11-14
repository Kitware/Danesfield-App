#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
###############################################################################




class RequestInfo:
    """
    Class to store HTTP request and authorization info.
    """
    def __init__(self, user, apiUrl, token):
        self.user = user
        self.apiUrl = apiUrl
        self.token = token
