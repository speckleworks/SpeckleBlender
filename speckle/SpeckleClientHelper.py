from speckle.api.SpeckleClient import SpeckleClient

'''
from json import JSONEncoder

def _default(self, obj):
    return getattr(obj.__class__, "to_json", _default.default)(obj)

_default.default = JSONEncoder().default  # Save unmodified default.
JSONEncoder.default = _default # replacement
'''

def GetAvailableStreams(client):
    if client is None: return None
    res = client.GetStreams()
    if res is not None:
        streams = {}
        for i in res.resources:
            streams[i.streamId] = i.name
        return streams
    return None

