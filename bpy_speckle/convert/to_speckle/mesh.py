import bpy, bmesh, struct

def export_mesh(blender_object, scale=1.0):
	return None

def MeshObject_to_SpeckleMesh(obj, scale=1.0):
    if obj.data.tessfaces is None or len(obj.data.tessfaces) < 1:
        obj.data.calc_tessface()
    verts = [x.co * scale for x in obj.data.vertices]

    # TODO: add n-gon support, using tessfaces for now
    faces = [x.vertices for x in obj.data.tessfaces]
    #faces = [x.vertices for x in obj.data.polygons]

    #sm = SpeckleResource.createSpeckleMesh()
    sm = {'vertices':[], 'faces':[]}

    for v in verts:
        sm['vertices'].extend(v)

    for f in faces:
        if len(f) == 3:
            sm['faces'].append(0)
        elif len(f) == 4:
            sm['faces'].append(1)
        else:
            continue

        sm['faces'].extend(f)

    # Add properties and custom data
    sm['properties'] = {}
    for key in obj.keys():
        #print (key)
        if key == "speckle" or key == "_RNA_UI":
            continue
        if hasattr(obj[key], 'to_dict'):
            sm['properties'][key] = obj[key].to_dict()
        else:            
            sm['properties'][key] = obj[key]

    # Set object transform
    sm['transform'] = [y for x in obj.matrix_world for y in x]
    #setattr(sm, 'transform', [y for x in obj.matrix_world for y in x])

    # This is still needed until there is a way to access the transform property in 
    # other programs.
    sm['properties']['transform'] = str([y for x in obj.matrix_world for y in x])
    #sm.properties['transform'] = [[y for y in x] for x in obj.matrix_world]

    # Add texture coordinates
    # TODO: make switchable

    # Using tessfaces for now - possible future n-gon support
    #if obj.data.uv_layers.active is not None:
    if obj.data.tessface_uv_textures.active is not None:
        uvs = [x.uv for x in obj.data.tessface_uv_textures.active.data]
        uv_string_list = ["%f %f" % (x[0][0], x[0][1]) for x in uvs]
        uv_string = ' '.join(uv_string_list)
        sm['properties']['texture_coordinates'] = base64.encodestring(uv_string.encode("utf-8")).decode("utf-8")

    sm['name'] = obj.name   
    sm['_id'] = obj.speckle.object_id
    sm['geometryHash'] = SetGeometryHash(str(sm))[:12]
    sm['hash'] = SetGeometryHash(str(sm) + strftime("%Y-%m-%d %H:%M:%S", gmtime()))[:12]
    sm['type'] = 'Mesh'
    sm['colors'] = []

    return sm	