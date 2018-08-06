#!/usr/bin/env python
# -*- coding: utf-8 -*-

##############################################################################
#  Copyright Kitware Inc.
#
#  Licensed under the Apache License, Version 2.0 ( the "License" );
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
##############################################################################

import os
import re


def removeDuplicateCount(name):
    """
    Remove duplicate count suffix from a name.
    For example, 'my_file (1).txt' becomes 'my_file.txt'.
    """
    return re.sub(r' \(\d+\)$', '', name)


def getPrefix(name):
    """
    Get common prefix from source image file name.
    """
    result = re.search(r'([0-9]{2}[A-Z]{3}[0-9]{8})[-_]', name)
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
    return removeDuplicateCount(item['name']).lower().endswith(extension)


def isMsiImage(item):
    """
    Return true if the item refers to an MSI image.

    :param item: Item document.
    :type item: dict
    """
    name = item['name'].lower()
    ext = os.path.splitext(name)[1]
    return '-m1bs-' in name and ext.startswith(('.ntf', '.tif'))


def isPanImage(item):
    """
    Return true if the item refers to a PAN image.

    :param item: Item document.
    :type item: dict
    """
    name = item['name'].lower()
    ext = os.path.splitext(name)[1]
    return '-p1bs-' in name and ext.startswith(('.ntf', '.tif'))
