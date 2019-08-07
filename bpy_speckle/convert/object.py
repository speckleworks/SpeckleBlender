import bpy

def add_material(smesh, blender_object):
        # Add material if there is one
    if 'properties' in smesh.keys()  and smesh['properties'] is not None:

        if 'material' in smesh['properties'].keys():
            material_name = smesh['properties']['material']['name']
            print ("bpySpeckle: Found material: %s" % material_name)

            mat = bpy.data.materials.get(material_name)

            if mat is None:
                mat = bpy.data.materials.new(name=material_name)
            blender_object.data.materials.append(mat)
            del smesh['properties']['material']


def try_add_property(speckle_object, blender_object, prop, prop_name):
    if prop in speckle_object.keys() and speckle_object[prop] is not None:
        blender_object[prop_name] = speckle_object[prop]


def add_dictionary(prop, blender_object, superkey):
    for key in prop.keys():
        if isinstance(prop[key], dict):
            add_dictionary(prop[key], blender_object, "{}.{}".format(superkey, key))
        else:
            blender_object["{}.{}".format(superkey, key)] = prop[key]

def add_custom_properties(speckle_object, blender_object):
    try_add_property(speckle_object, blender_object, 'type', 'speckle_type')
    try_add_property(speckle_object, blender_object, 'transform', 'speckle_transform')
    try_add_property(speckle_object, blender_object, 'name', 'speckle_name')

    if 'properties' in speckle_object.keys()  and speckle_object['properties'] is not None:
        for key in speckle_object['properties'].keys():
            attr = speckle_object['properties'][key]
            if isinstance(attr, dict):
                add_dictionary(attr, blender_object, "{}.{}".format('properties', key))
            else:
                blender_object['properties.' + key] = attr