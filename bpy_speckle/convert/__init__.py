from .mesh import import_mesh
from .curve import import_curve, import_line, import_polyline, import_polycurve
from .brep import import_brep
from .default import import_default

def import_null(speckle_object, scale):
    print(speckle_object['type'])
    print(speckle_object)
    print()

CONVERT = {
    "Mesh": import_mesh, 
    "Brep": import_brep,
    "Curve": import_curve,
    "Line": import_curve,
    "Polyline": import_curve,
    "Polycurve":import_curve,
    "Arc":import_curve,
    "default":import_default
}

def from_speckle_object(speckle_object, scale):
    if "type" in speckle_object.keys():
        speckle_type = speckle_object["type"]

        if speckle_type in CONVERT.keys():
            return CONVERT[speckle_type](speckle_object, scale)
        else:
            return CONVERT['default'](speckle_object, scale)

    return None
