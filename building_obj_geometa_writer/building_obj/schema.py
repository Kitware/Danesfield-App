from marshmallow import fields
from bson.objectid import ObjectId
import json
import re
from pyproj import Proj

from geometa.schema import BaseSchema
from geometa import from_bounds_to_geojson, CannotHandleError
from shapely.geometry import MultiPoint
from girder.models.item import Item
from girder.models.file import File


class OBJSchema(BaseSchema):
    driver = fields.String(required=True)


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


def getOBJBounds(objFileName, offset):
    # Read vertices in OBJ file
    points = list(readObjFileVertices(objFileName))

    # Compute bounds
    multiPoint = MultiPoint(points)
    bounds = multiPoint.bounds

    # Apply offset to bounds
    return {
        "left": bounds[0] + offset[0],
        "bottom": bounds[1] + offset[1],
        "right": bounds[2] + offset[0],
        "top": bounds[3] + offset[1]
    }


def handler(path, girder_item, girder_file):
    if ".obj" not in girder_file['name'] and \
            ".OBJ" not in girder_file['name']:
        raise CannotHandleError(girder_file['name'] + ' is not an OBJ file')
    try:
        jsonItem = Item().findOne({'name': girder_file['name'].replace(
            "obj", "json"), 'folderId': girder_item['folderId']})
        jsonFile = [i for i in Item().childFiles(jsonItem, limit=1)][0]
        jsonContent = json.loads(''.join(list(File().download(jsonFile, headers=False)())))
        projectionParams = jsonContent['scenes'][0]['coordinate_system']['parameters']
        ellps = projectionParams[0].upper()
        m = re.compile('(utm) zone ([0-9]+)N', re.IGNORECASE).match(projectionParams[1])
        proj = m.group(1).lower()
        zone = m.group(2)
        sourceSrs = Proj(proj=proj, zone=zone, ellps=ellps).srs
        offset = [projectionParams[2], projectionParams[3], projectionParams[4]]
        bounds = getOBJBounds(path, offset)
        geoJsonBounds = from_bounds_to_geojson(bounds, sourceSrs)
        geometa = {
            'crs': sourceSrs,
            'nativeBounds': bounds,
            'bounds': geoJsonBounds,
            'type_': 'vector',
            'driver': 'OBJ'
        }
        schema = OBJSchema()
        return schema.load(geometa)
    except Exception:
        raise CannotHandleError('Failed to add geometa to OBJ file' + girder_file['name'])
