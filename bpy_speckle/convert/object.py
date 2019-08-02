import bpy

def add_material(smesh, bobj):
        # Add material if there is one
    if 'properties' in smesh.keys()  and smesh['properties'] is not None:

        if 'material' in smesh['properties'].keys():
            material_name = smesh['properties']['material']['name']
            print ("bpySpeckle: Found material: %s" % material_name)

            mat = bpy.data.materials.get(material_name)

            if mat is None:
                mat = bpy.data.materials.new(name=material_name)
            bobj.data.materials.append(mat)
            del smesh['properties']['material']

def add_custom_properties(smesh, bobj):
    if 'properties' in smesh.keys()  and smesh['properties'] is not None:
        for key in smesh['properties'].keys():
            attr = smesh['properties'][key]
            bobj[key] = attr