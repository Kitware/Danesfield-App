import json
from bson import ObjectId

from girder.api import access
from girder.api.describe import autoDescribeRoute, Description
from girder.constants import AccessType
from girder.api.rest import Resource
from girder.models.file import File
from girder.models.item import Item
from ..models.filter import Filter


class DatasetResource(Resource):

    def __init__(self):
        super(DatasetResource, self).__init__()

        self.resourceName = 'dataset'
        self.route('GET', (), self.getAll)
        self.route('GET', (':id',), self.get)
        self.route('GET', ('bounds',), self.getAllBounds)

    @autoDescribeRoute(
        Description('')
        .errorResponse()
        .errorResponse('Read access was denied on the item.', 403)
    )
    @access.user
    def getAll(self, params):
        return self._getAll()

    def _getAll(self):
        datasetItems = list(Item().find({'geometa.driver': {'$in': ['GeoJSON', 'GeoTIFF']}}))
        return datasetItems

    @autoDescribeRoute(
        Description('')
        .modelParam('id', model=Item, level=AccessType.READ)
        .errorResponse()
        .errorResponse('Read access was denied on the item.', 403)
    )
    @access.user
    def get(self, item, params):
        return item

    @autoDescribeRoute(
        Description('')
        .errorResponse()
        .errorResponse('Read access was denied on the item.', 403)
    )
    @access.user
    def getAllBounds(self, params):
        datasetItems = self._getAll()
        datasetBounds = [{
            'name': item['name'],
            'bounds': item['geometa']['bounds']
        } for item in datasetItems]
        return datasetBounds
