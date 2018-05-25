import json
from speckle.api.SpeckleClient import SpeckleResource

class SpeckleLayerProperties(object):
    color = ""
    visible = True
    pointsize = 1.0
    linewidth = 0.25
    shininess = 0.5
    smooth = False
    showEdges = True
    wireframe = True

    def __init__(self, j = None):
        if j is not None:
            self.from_json(j)

    def to_json(self):
        return json.dumps(self.__dict__, sort_keys = True)

    def from_json(self, j):
        if type(j) is dict:
            self.__dict__ = j
        elif j.__class__.__name__ == "SpeckleResource":
            self.__dict__ = SpeckleResource.to_dict(j)
        else:
            self.__dict__ = json.loads(j)

class SpeckleLayer(object):
    name = ""
    guid = []
    orderIndex = 0
    startIndex = 0
    objectCount = 0
    topology = ""
    properties = SpeckleLayerProperties()

    def __init__(self, j = None):
        if j is not None:
            self.from_json(j)
        else:
            self.name = "SpeckleLayer"

    def to_json(self):
        return json.dumps(self.__dict__, sort_keys = True)

    def from_json(self, j):
        if type(j) is dict:
            self.__dict__ = j
        elif j.__class__.__name__ == "SpeckleResource":
            self.__dict__ = SpeckleResource.to_dict(j)            
        else:
            self.__dict__ = json.loads(j)

