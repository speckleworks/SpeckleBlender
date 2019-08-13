import bpy
from .mesh import to_bmesh
from .object import add_custom_properties, add_material

def import_brep(speckle_brep, scale):

    if 'geometryHash' in speckle_brep and speckle_brep['geometryHash'] is not None:
        name = speckle_brep['geometryHash']
    else:
        name = speckle_brep['_id']

    dvKey = ""
    if "displayValue" in speckle_brep.keys():
        dvKey = "displayValue"
    elif "displayvalue" in speckle_brep.keys():
        dvKey = "displayvalue"

    if dvKey != "":
        mesh = to_bmesh(speckle_brep[dvKey], name, scale)
        add_custom_properties(speckle_brep[dvKey], mesh)

    else:
        mesh = None

    name = speckle_brep['_id']
    obj = bpy.data.objects.new(name, mesh)

    obj.speckle.object_id = speckle_brep['_id']
    obj.speckle.enabled = True

    add_material(speckle_brep, obj)
    add_custom_properties(speckle_brep, obj)

    return obj