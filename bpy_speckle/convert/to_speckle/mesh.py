import bpy, bmesh, struct

import base64, hashlib
from time import strftime, gmtime

import speckle.schemas

def export_mesh(blender_object, scale=1.0):
    return MeshObject_to_SpeckleMesh(blender_object, scale)
	#return None

def SetGeometryHash(data):
    code = hashlib.md5(data.encode('utf-8')).hexdigest()
    return code

def MeshObject_to_SpeckleMesh(obj, scale=1.0):
    if obj.data.loop_triangles is None or len(obj.data.loop_triangles) < 1:
        obj.data.calc_loop_triangles()
    verts = [x.co * scale for x in obj.data.vertices]

    # TODO: add n-gon support, using tessfaces for now
    faces = [x.vertices for x in obj.data.loop_triangles]

    #faces = [x.vertices for x in obj.data.polygons]

    sm = speckle.schemas.Mesh()

    for v in verts:
        sm.vertices.extend(v)

    for f in faces:
        if len(f) == 3:
            sm.faces.append(0)
        elif len(f) == 4:
            sm.faces.append(1)
        else:
            continue

        sm.faces.extend(f)

    # Add texture coordinates
    # TODO: make switchable

    # Using tessfaces for now - possible future n-gon support
    #if obj.data.uv_layers.active is not None:

    '''
    if obj.data.tessface_uv_textures.active is not None:
        uvs = [x.uv for x in obj.data.tessface_uv_textures.active.data]
        uv_string_list = ["%f %f" % (x[0][0], x[0][1]) for x in uvs]
        uv_string = ' '.join(uv_string_list)
        sm['properties']['texture_coordinates'] = base64.encodestring(uv_string.encode("utf-8")).decode("utf-8")
    '''

    sm.name = obj.name   
    #sm.id = obj.speckle.object_id
    #sm.geometryHash = SetGeometryHash(str(sm))[:12]
    #sm.hash = SetGeometryHash(str(sm) + strftime("%Y-%m-%d %H:%M:%S", gmtime()))[:12]
    sm.colors = []

    return sm	