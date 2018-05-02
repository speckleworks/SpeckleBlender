from .SpeckleClient import SpeckleClient

def GetAvailableStreams(client):
    if client is None: return None
    res = client.GetStreams()
    if res is not None:
        streams = {}
        for i in res['resources']:
            streams[i['streamId']] = i['name']
        return streams
    return None
