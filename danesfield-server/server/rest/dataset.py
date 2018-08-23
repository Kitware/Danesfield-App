from bson import ObjectId

from girder.api import access
from girder.api.describe import autoDescribeRoute, Description
from girder.constants import AccessType
from girder.api.rest import Resource
from girder.models.item import Item
from ..models.workingSet import WorkingSet


class DatasetResource(Resource):

    def __init__(self):
        super(DatasetResource, self).__init__()

        self.resourceName = 'dataset'
        self.route('GET', (), self.getAll)
        self.route('GET', (':id',), self.get)
        self.route('GET', ('bounds',), self.getAllBounds)
        self.route('GET', ('workingset',':id',), self.getWorkingSetDatasets)

    @autoDescribeRoute(
        Description('')
        .errorResponse()
        .errorResponse('Read access was denied on the item.', 403)
    )
    @access.user
    def getAll(self, params):
        return self._getAll()

    def _getAll(self):
        datasetItems = list(Item().find(
            {'$or':[{'geometa.driver': {'$in': ['GeoJSON', 'GeoTIFF', 'OBJ', 'National Imagery Transmission Format']}},{'geometa.subDatasets.driver':'National Imagery Transmission Format'}]}))
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

    @autoDescribeRoute(
        Description('')
        .modelParam('id', model=WorkingSet, destName='workingSet')
        .errorResponse()
        .errorResponse('Read access was denied on the item.', 403)
    )
    @access.user
    def getWorkingSetDatasets(self, workingSet, params):
        datasetItems = list(Item().find(
            {"_id":{"$in":[ObjectId(id) for id in workingSet['datasetIds']]}}))
        return datasetItems
