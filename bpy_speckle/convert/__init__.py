from .from_speckle import *
from .to_speckle import *

FROM_SPECKLE = {
    "Mesh": import_mesh, 
    "Brep": import_brep,
    "Curve": import_curve,
    "Line": import_curve,
    "Polyline": import_curve,
    "Polycurve":import_curve,
    "Arc":import_curve,
    "default":import_default
}

TO_SPECKLE = {
    "MESH": export_mesh,
    "CURVE": export_curve,
    "EMPTY": export_empty,
    "default": export_default
}

def from_speckle_object(speckle_object, scale):
    if "type" in speckle_object.keys():
        speckle_type = speckle_object["type"]

        if speckle_type in FROM_SPECKLE.keys():
            return FROM_SPECKLE[speckle_type](speckle_object, scale)
        else:
            return FROM_SPECKLE['default'](speckle_object, scale)

    return None

def to_speckle_object(blender_object, scale):
    blender_type = blender_object.type

    if blender_type in TO_SPECKLE.kets():
        return TO_SPECKLE[blender_type](blender_object, scale)

