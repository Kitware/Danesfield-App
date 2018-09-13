#!/usr/bin/env python

"""
Set geospatial metadata on a Girder item for an OBJ file.

Requires information from 3 files:
- The OBJ file.
- A text file containing 3 lines with floating point values that indicate a
  global (x, y, z), offset.
- A reference GeoTIFF image in the AOI from which to get the source coordinate
  reference system.

Requires Python 3.

Tip to install gdal Python bindings on Ubuntu using pip:

Install the following packages:
- libgdal-dev
- python3-dev

Run:
  pip install --global-option=build_ext --global-option="-I/usr/include/gdal" GDAL==$(gdal-config --version)
"""

import argparse
import gdal
import girder_client
import json
import logging
import os
import osr
import pyproj
import shapely
import sys
import tempfile

from shapely.geometry import MultiPoint
from pathlib import Path


def readOffsetFile(name):
    """
    Read offset file with three floating point numbers representing x, y, and z
    offsets on separate lines.
    """
    offsets = []
    with open(name, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            offsets.append(float(line))

    if len(offsets) != 3:
        raise RuntimeError('Offset file must contain 3 floating point values')

    return offsets


def readObjFileVertices(name):
    """
    Read the vertices from an OBJ file. Returns a generator that yields each (x,y,z) vertex.
    """
    with open(name, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            if line.startswith('v '):
                line = line.strip()
                coords = line[2:].split(' ')
                if len(coords) != 3:
                    raise RuntimeError('Vertex definition must contain 3 floating point values')
                coords = [float(coord) for coord in coords]
                yield coords
                continue


def getProjection(name):
    """
    Get the projection from a geospatial image file. Returns a PROJ.4 string.
    """
    image = gdal.Open(name, gdal.GA_ReadOnly)
    if image is None:
        raise RuntimeError('Unable to open image')
    projection = image.GetProjection()
    srs = osr.SpatialReference(wkt=projection)
    return pyproj.Proj(srs.ExportToProj4())


# From https://github.com/OpenGeoscience/girder_geospatial/blob/9c928d5/geometa/__init__.py#L12
def clamp(number, lowerBound, upperBound):
    return max(lowerBound, min(number, upperBound))


# Based on https://github.com/OpenGeoscience/girder_geospatial/blob/9c928d5/geometa/__init__.py#L16
def boundsToGeoJson(bounds, sourceProj, destProj):
    LONGITUDE_RANGE = (-180.0, 180.0)
    LATITUDE_RANGE = (-90.0, 90.0)
    try:
        xmin, ymin = pyproj.transform(sourceProj, destProj, *bounds[:2])
        xmax, ymax = pyproj.transform(sourceProj, destProj, *bounds[2:])
        wgs84_bounds = shapely.geometry.Polygon.from_bounds(
            clamp(xmin, *LONGITUDE_RANGE),
            clamp(ymin, *LATITUDE_RANGE),
            clamp(xmax, *LONGITUDE_RANGE),
            clamp(ymax, *LATITUDE_RANGE))
        return shapely.geometry.mapping(wgs84_bounds)
    except RuntimeError:
        return ''


def getGeospatialMetadata(sourceProj, destProj, offsetFileName, objFileName):
    """
    Get geospatial metadata object compatible with the girder_geospatial plugin schema.

    :param sourceProj: Source projection
    :type sourceProj: pyproj.Proj
    :param destProj: Destination projection
    :type destProj: pyproj.Proj
    :param offsetFileName: Name of offset file
    :type offsetFileName: str
    :param objFileName: Name of OBJ file
    :type objFileName: str
    """
    # Read vertices in OBJ file
    points = list(readObjFileVertices(objFileName))

    # Read offset from text file
    offset = readOffsetFile(offsetFileName)

    # Compute bounds
    multiPoint = MultiPoint(points)
    bounds = multiPoint.bounds

    # Apply offset to bounds
    offsetBounds = [
        bounds[0] + offset[0],
        bounds[1] + offset[1],
        bounds[2] + offset[0],
        bounds[3] + offset[1]
    ]

    # Compute GeoJSON bounds in destination projection
    geoJsonBounds = boundsToGeoJson(offsetBounds, sourceProj, destProj)

    return {
        'crs': sourceProj.srs,
        'nativeBounds': {
            'left': offsetBounds[0],
            'bottom': offsetBounds[1],
            'right': offsetBounds[2],
            'top': offsetBounds[3]
        },
        'bounds': geoJsonBounds,
        'type_': 'vector',
        'driver': 'OBJ'
    }


def main(args):
    # Configure argument parser
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--api-url',
        type=str,
        required=True,
        help='Girder API URL')
    parser.add_argument(
        '--obj-file-id',
        type=str,
        required=True,
        help='OBJ file ID')
    parser.add_argument(
        '--offset-file-id',
        type=str,
        required=True,
        help='Offset text file ID')
    parser.add_argument(
        '--tiff-file-id',
        type=str,
        required=True,
        help='GeoTIFF file ID of image in AOI')

    # Parse arguments
    args = parser.parse_args(args)

    # Get Girder API key from environment
    apiKey = os.environ.get('GIRDER_API_KEY')
    if apiKey is None:
        raise RuntimeError('GIRDER_API_KEY environment variable must be set')

    # Create and authenticate Girder client
    client = girder_client.GirderClient(apiUrl=args.api_url)
    client.authenticate(apiKey=apiKey)

    # Download files to temporary directory
    with tempfile.TemporaryDirectory(prefix='obj-geospatial-metadata-') as tempDir:
        tempDirPath = Path(tempDir)

        objFileName = (tempDirPath / 'model.obj').as_posix()
        offsetFileName = (tempDirPath / 'offset.txt').as_posix()
        tiffFileName = (tempDirPath / 'image.tiff').as_posix()

        client.downloadFile(args.obj_file_id, path=objFileName)
        client.downloadFile(args.offset_file_id, path=offsetFileName)
        client.downloadFile(args.tiff_file_id, path=tiffFileName)

        # Get source projection from image
        sourceProj = getProjection(tiffFileName)

        # Destination projection
        destProj = pyproj.Proj(init='epsg:4326')

        logging.info('sourceProj: {}'.format(sourceProj.srs))
        logging.info('destProj: {}'.format(destProj.srs))

        # Get geospatial metadata
        metadata = getGeospatialMetadata(sourceProj, destProj, offsetFileName, objFileName)

        logging.info('geometa:\n{}'.format(json.dumps(metadata, indent=4)))

        # Update item's geospatial metadata
        objFile = client.getFile(args.obj_file_id)
        client.put('/item/{}/geometa'.format(objFile['itemId']), parameters={
            'geometa': json.dumps(metadata)
        })


if __name__ == '__main__':
    loglevel = os.environ.get('LOGLEVEL', 'WARNING').upper()
    logging.basicConfig(level=loglevel)

    main(sys.argv[1:])
