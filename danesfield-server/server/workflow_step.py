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

from girder.models.item import Item

from .workflow import DanesfieldWorkflowException
from .workflow_utilities import fileFromItem


class DanesfieldWorkflowStep(object):
    """
    Class to define a step in the Danesfield workflow.
    """
    def __init__(self, name):
        self.name = name
        self.dependencies = set()

    def addDependency(self, name):
        """
        Add a dependency to indicate that this step depends on the output of another step.
        """
        self.dependencies.add(name)

    def run(self, jobInfo):
        """
        Run the step. Subclasses must implement this method.

        :param jobInfo: The job context in which to run the step.
        :type jobInfo: JobInfo
        """
        raise NotImplementedError('Implement in subclass')

    def getSingleFile(self, workingSet, condition=None):
        """
        Get a single file from a working set. An exception is raised if the
        working set is empty, contains more than one item, or if the item
        contains more than one file.

        :param workingSet: The working set containing the file.
        :type workingSet: dict
        :param condition: An optional condition that items in the working set must meet.
        :type condition: callable
        """
        items = [
            item
            for item in (
                Item().load(itemId, force=True, exc=True)
                for itemId in workingSet['datasetIds']
            )
            if condition is None or condition(item)
        ]
        if not items:
            raise DanesfieldWorkflowException('Unable to find file', step=self.name)
        if len(items) > 1:
            raise DanesfieldWorkflowException('Expected only one file, got {}'.format(len(items)),
                                              step=self.name)
        return fileFromItem(items[0])

    def getFiles(self, workingSet, condition=None):
        """
        Get files from a working set.

        :param workingSet: The working set containing the files.
        :type workingSet: dict
        :param condition: An optional condition that items in the working set must meet.
        :type condition: callable
        """
        files = [
            fileFromItem(item)
            for item in (
                Item().load(itemId, force=True, exc=True)
                for itemId in workingSet['datasetIds']
            )
            if condition is None or condition(item)
        ]

        return files
