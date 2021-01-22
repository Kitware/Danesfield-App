###############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
###############################################################################

import os
from girder.utility.webroot import WebrootBase
from girder import constants


class ClientWebroot(WebrootBase):
    def __init__(self, templatePath=None):
        super(ClientWebroot, self).__init__("")

        self.vars = {
            # 'title' is deprecated use brandName instead
            "title": "Girder"
        }

    def GET(self, **params):
        file = open(
            os.path.join(
                constants.STATIC_ROOT_DIR,
                "clients",
                "web",
                "static",
                "core3d",
                "index.html",
            ),
            "r",
        )
        return file.read()

    def DELETE(self, **params):
        raise Exception(405)

    def PATCH(self, **params):
        raise Exception(405)

    def POST(self, **params):
        raise Exception(405)

    def PUT(self, **params):
        raise Exception(405)
