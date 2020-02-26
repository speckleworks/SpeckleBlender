import bpy
from mathutils import Matrix

from .from_speckle import *
from .to_speckle import *
from bpy_speckle.util import find_key_case_insensitive


FROM_SPECKLE = {
    "Mesh": import_mesh, 
    "Brep": import_brep,
    "Curve": import_curve,
    "Line": import_curve,
    "Polyline": import_curve,
    "Polycurve":import_curve,
    "Arc":import_curve,
}

TO_SPECKLE = {
    "MESH": export_mesh,
    "CURVE": export_curve,
    "EMPTY": export_empty,
}

def set_transform(speckle_object, blender_object):

    transform = find_key_case_insensitive(speckle_object, "transform")
    if transform:
        if len(transform) == 16:
            mat = Matrix(
                list1=transform[0:3],
                list2=transform[4:7],
                list3=transform[8:11],
                list4=transform[12:15]
                )
            blender_object.matrix_world = mat

def add_material(smesh, blender_object):
        # Add material if there is one
    props = find_key_case_insensitive(smesh, "properties")
    if props:
        material = find_key_case_insensitive(props, "material")
        if material:
            material_name = material.get('name', None)
            if material_name:
                print ("bpySpeckle: Found material: %s" % material_name)

                mat = bpy.data.materials.get(material_name)

                if mat is None:
                    mat = bpy.data.materials.new(name=material_name)
                blender_object.data.materials.append(mat)
                #del smesh['properties']['material']
                del material


def try_add_property(speckle_object, blender_object, prop, prop_name):
    if prop in speckle_object.keys() and speckle_object[prop] is not None:
        blender_object[prop_name] = speckle_object[prop]


def add_dictionary(prop, blender_object, superkey=None):
    for key in prop.keys():
        key_name = "{}.{}".format(superkey, key) if superkey else "{}".format(key)
        if isinstance(prop[key], dict):
            subtype = prop[key].get("type", None)
            if subtype and subtype in FROM_SPECKLE.keys():
                continue
            else:
                add_dictionary(prop[key], blender_object, key_name)
        else:
            blender_object[key_name] = prop[key]

def add_custom_properties(speckle_object, blender_object):
    try_add_property(speckle_object, blender_object, 'type', '_speckle_type')
    try_add_property(speckle_object, blender_object, 'transform', '_speckle_transform')
    try_add_property(speckle_object, blender_object, 'name', '_speckle_name')

    properties = speckle_object.get("properties", None)
    if properties:
        add_dictionary(properties, blender_object, "")

def from_speckle_object(speckle_object, scale, name=None):

    speckle_type = speckle_object.get("type", None)

    if speckle_type:
        speckle_id = speckle_object.get("_id", "")

        if name:
            speckle_name = name
        elif speckle_id:
            speckle_name = speckle_id
        else:
            speckle_name = "Unidentified Speckle Object"

        if speckle_type in FROM_SPECKLE.keys():
            obdata = FROM_SPECKLE[speckle_type](speckle_object, scale, speckle_name)
        else:
            print("Failed to convert {} type".format(speckle_type))
            obdata = None

        if speckle_name in bpy.data.objects.keys():
            blender_object = bpy.data.objects[speckle_name]
            blender_object.data = obdata
            if hasattr(obdata, "materials"):
                blender_object.data.materials.clear()
        else:
            blender_object = bpy.data.objects.new(speckle_name, obdata) 


        blender_object.speckle.object_id = speckle_object.get('_id', "")
        blender_object.speckle.enabled = True

        add_custom_properties(speckle_object, blender_object)
        add_material(speckle_object, blender_object)
        set_transform(speckle_object, blender_object)

        return blender_object             

    return None

def get_speckle_subobjects(attr, scale, name):

    subobjects = []
    for key in attr.keys():
        if isinstance(attr[key], dict):
            subtype = attr[key].get("type", None)
            if subtype:
                name = "{}.{}".format(name, key)
                #print("{} :: {}".format(name, subtype))
                subobject = from_speckle_object(attr[key], scale, name)
                add_custom_properties(attr[key], subobject)

                subobjects.append(subobject)
                props = attr[key].get("properties", None)
                if props:
                    subobjects.extend(get_speckle_subobjects(props, scale, name))

    return subobjects

def to_speckle_object(blender_object, scale):
    blender_type = blender_object.type

    if blender_type in TO_SPECKLE.keys():
        return TO_SPECKLE[blender_type](blender_object, scale)

