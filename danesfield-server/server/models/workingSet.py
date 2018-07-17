from girder.models.model_base import Model


class WorkingSet(Model):

    def initialize(self):
        self.name = 'workingSet'
        self.ensureIndex('name')
        self.ensureIndex('parentWorkingSetId')

    def validate(self, model):
        return model
