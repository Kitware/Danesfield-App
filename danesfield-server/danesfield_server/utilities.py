#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
###############################################################################

import re


def removeDuplicateCount(name):
    """
    Remove duplicate count suffix from a name.
    For example, 'my_file (1).txt' becomes 'my_file.txt'.
    """
    return re.sub(r" \(\d+\)$", "", name)


def getPrefix(name):
    """
    Get common prefix from source image file name.
    """
    result = re.search(r"([0-9]{2}[A-Z]{3}[0-9]{8})[-_]", name)
    return None if not result else result.group(1)


def hasExtension(item, extension):
    """
    Return true if the item's name has the specified extension.
    Ignores duplicate count suffixes.

    :param item: Item document.
    :type item: dict
    :param extension: The file extension, including a leading period.
    :type extension: str
    """
    return removeDuplicateCount(item["name"]).lower().endswith(extension)
