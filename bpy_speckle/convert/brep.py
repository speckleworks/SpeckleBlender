import bpy
from .mesh import to_bmesh
from .object import add_custom_properties, add_material

def import_brep(speckle_brep, scale):
    name = speckle_brep['_id']

    dvKey = ""
    if "displayValue" in speckle_brep.keys():
        dvKey = "displayValue"
    elif "displayvalue" in speckle_brep.keys():
        dvKey = "displayvalue"

    if dvKey != "":
        mesh = to_bmesh(speckle_brep[dvKey], name, scale)

    obj = bpy.data.objects.new(name, mesh)

    obj.speckle.object_id = speckle_brep['_id']
    obj.speckle.enabled = True

    add_material(speckle_brep, obj)
    add_custom_properties(speckle_brep, obj)

    return obj