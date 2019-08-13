import bpy
from .object import add_custom_properties, add_material

def import_default(speckle_object, scale):
    if 'name' in speckle_object and speckle_object['name'] is not None:
        name = speckle_object['name']
    else:
        name = speckle_object['_id']

    obj = bpy.data.objects.new(name, None)

    obj.speckle.object_id = speckle_object['_id']
    obj.speckle.enabled = True

    add_custom_properties(speckle_object, obj)

    return obj

def export_default(blender_object, scale=1.0):
    return None    