###############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
###############################################################################

from setuptools import setup, find_packages

setup(
    name="danesfield-server",
    version="0.0.0.dev1",
    description="",
    url="",
    python_requires="~=3.7",
    install_requires=[
        "numpy>=1.20.1",
        "utm>=0.7.0",
        "girder>=3.1.3",
        "girder_jobs>=3.1.3",
        "girder-worker>=0.8.0",
        "girder-large-image>=1.3.2",
        "large-image-source-gdal>=1.3.2",
        "girder-geospatial>=0.3.1",
        "girder-geospatial-grid>=0.1.0",
        "girder-geospatial-raster>=0.1.0",
        "girder-geospatial-vector>=0.1.0",
        "girder-resource-path-tools>=0.0.0",
    ],
    entry_points={
        "girder.plugin": ["danesfield = danesfield_server:DanesfieldPlugin"],
    },
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
