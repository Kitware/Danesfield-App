###############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
###############################################################################

import re
from setuptools import setup, find_packages

requires = []
dep_links = []
# parse requirements file
with open("requirements.txt") as f:
    comment = re.compile("(^#.*$|\s+#.*$)")
    for line in f.readlines():
        line = line.strip()
        line = comment.sub("", line)
        if line:
            if line.startswith("git+") and "#egg=" in line:
                dep_links.append(line)
                requires.append(line.split("#egg=", 1)[1].replace("-", "=="))
            else:
                requires.append(line)

setup(
    name="danesfield-server",
    version="0.0.0.dev1",
    description="",
    url="",
    python_requires="~=3.8",
    install_requires=[
        "girder>=3.1.3",
        "girder_jobs>=3.1.3",
        "girder-worker>=0.8.0",
        "girder-geospatial>=0.2.0",
        "girder-geospatial>=0.2.0",
        "girder-geospatial-grid>=0.1.0",
        "girder-geospatial-raster>=0.1.0",
        "girder-geospatial-vector>=0.1.0",
    ],
    entry_points={
        "girder.plugin": ["danesfield = danesfield_server:DanesfieldPlugin"],
    },
    dependency_links=dep_links,
    author="Kitware Inc",
    author_email="",
    license="",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: Apache Software License"
        "Topic :: Scientific/Engineering :: GIS",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Programming Language :: Python",
    ],
    packages=find_packages(exclude=["tests*", "server*", "docs"]),
    zip_safe=False,
)
