from girder.models.model_base import Model


class Filter(Model):

    def initialize(self):
        self.name = 'filter'

    def validate(self, model):
        return model
