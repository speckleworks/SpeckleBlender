import json

class SpeckleResource(object):
    def __init__(self, d):
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
               setattr(self, a, [SpeckleResource(x) if isinstance(x, dict) else x for x in b])
            else:
               setattr(self, a, SpeckleResource(b) if isinstance(b, dict) else b)

    @staticmethod
    def to_dict(obj):
        '''
        from https://stackoverflow.com/questions/1036409/recursively-convert-python-object-graph-to-dictionary
        '''
        if isinstance(obj, dict):
            data = {}
            for (k, v) in obj.items():
                data[k] = SpeckleResource.to_dict(v)
            return data
        elif isinstance(obj, (list, tuple)):
            return [SpeckleResource.to_dict(v) for v in obj]
        #elif hasattr(obj, "_ast"):
        #    return SpeckleResource.to_dict(obj._ast())
        #elif hasattr(obj, "__iter__"):
        #    return [SpeckleResource.to_dict(v) for v in obj]        
        elif hasattr(obj, "__dict__"):
            data = dict([(key, SpeckleResource.to_dict(value))
                         for key, value in obj.__dict__.items()
                         #if not callable(value) and not key.startswith('_') and key not in ['_name']])
                         if not callable(value)])
            #if hasattr(obj, "__class__"):
            #    data['SpeckleResource'] = obj.__class__.__name__
            return data
        else:
            return obj

    @staticmethod
    def to_json(obj):
        return json.dumps(SpeckleResource.to_dict(obj), sort_keys=True)

    @staticmethod
    def to_json_pretty(obj):
        return json.dumps(SpeckleResource.to_dict(obj), indent=4, sort_keys=True)


    @staticmethod
    def isSpeckleObject(obj):
        if (hasattr(obj, 'type') and
        hasattr(obj, '_id') and
        hasattr(obj, 'hash') and
        hasattr(obj, 'geometryHash') and
        hasattr(obj, 'applicationId') and
        hasattr(obj, 'properties')):
            return True
        return False

    @staticmethod
    def createSpeckleObject():
        attr = {'type':None,'_id':None, 'hash':1234, 'geometryHash':None,'applicationId':None, 'properties':None}
        return SpeckleResource(attr)

    @staticmethod
    def isSpeckleMesh(obj):
        if (hasattr(obj, 'type') and
        hasattr(obj, '_id') and
        hasattr(obj, 'hash') and
        hasattr(obj, 'geometryHash') and
        hasattr(obj, 'applicationId') and
        hasattr(obj, 'vertices') and
        hasattr(obj, 'faces') and
        hasattr(obj, 'colors') and
        hasattr(obj, 'properties')):
            return True
        return False

    @staticmethod
    def createSpeckleMesh():
        attr = {'type':'Mesh','_id':None, 'hash':1234, 'geometryHash':None,'applicationId':'Blender', 'properties':None,
        'vertices':[], 'faces':[], 'colors':[]}
        return SpeckleResource(attr)

    @staticmethod
    def isSpecklePlaceholder(obj):
        print ("TODO: implement SpeckleResource.isSpecklePlaceholder")
        return

    @staticmethod
    def createSpecklePlaceholder(id = None):
        attr = {'type':'Placeholder','_id':id}
        return SpeckleResource(attr)

    @staticmethod
    def isSpeckleLayerProperties(obj):
        print ("TODO: implement SpeckleResource.isSpeckleLayerProperties")
        return

    @staticmethod
    def createSpeckleLayerProperties():
        attr = {'color':'','visible':True, 'pointsize':1.0, 'linewidth':0.25, 'shininess':0.5, 
        'smooth':False,'showEdges':True, 'wireframe':True}
        return SpeckleResource(attr)

    @staticmethod
    def isSpeckleLayer(obj):
        print ("TODO: implement SpeckleResource.isSpeckleLayer")
        return

    @staticmethod
    def createSpeckleLayer():
        attr = {'name':'SpeckleLayer', 'guid':None, 'orderIndex':0, 'startIndex':0, 'objectCount':0, 
        'topology':'', 'properties':SpeckleResource.createSpeckleLayerProperties()}
        return SpeckleResource(attr)

    @staticmethod
    def isSpeckleStream(obj):
        print ("TODO: implement SpeckleResource.isSpeckleStream")
        return

    @staticmethod
    def createSpeckleStream():
        attr = {'streamId':'', 'name':'SpeckleStream', 'objects':[], 'layers':[], 'baseProperties':None, 
        'globalMeasures':None, 'isComputedResult':False, 'viewerLayers':[], 'parent':'', 
        'children':[], 'ancestors':[]}
        return SpeckleResource(attr)

    @staticmethod
    def createSpeckleStreamUpdate():
        attr = {'objects':[], 'layers':[]}
        return SpeckleResource(attr)