import bpy, bmesh
import base64

from .SpeckleObject import SpeckleMesh
from .util import SPrint

def SpeckleMesh_to_Lists(o):
    verts = []
    faces = []
    uv = []

    if 'texture_coordinates' in o['properties']:
        #s_uvs = o['properties']['texture_coordinates']
        decoded = base64.b64decode(o['properties']['texture_coordinates']).decode("utf-8")
        s_uvs = decoded.split()   
          
        for i in range(0, len(s_uvs), 2):
            uv.append((float(s_uvs[i]), float(s_uvs[i+1])))
    
    if 'vertices' in o:
        s_verts = o['vertices']
        for i in range(0, len(s_verts), 3):
            verts.append((float(s_verts[i]), float(s_verts[i + 1]), float(s_verts[i + 2])))
        
    if 'faces' in o:
        s_faces = o['faces']
        i = 0
        while (i < len(s_faces)):
            if (s_faces[i] == 0):
                i += 1
                faces.append((int(s_faces[i]), int(s_faces[i + 1]), int(s_faces[i + 2])))
                i += 3
            elif (s_faces[i] == 1):
                i += 1
                faces.append((int(s_faces[i]), int(s_faces[i + 1]), int(s_faces[i + 2]), int(s_faces[i + 3])))
                i += 4
            else:
                print("Invalid face length.\n" + str(s_faces[i]))
                return

    return verts, faces, uv

def Lists_to_Mesh(verts, faces, uv, name, scale=1.0):
    bm = bmesh.new()
    
    # Make verts
    for v in verts:
        bm.verts.new(tuple([x * scale for x in v]))
        
    bm.verts.ensure_lookup_table()

    # Make faces
    for f in faces:
            bm.faces.new([bm.verts[x] for x in f])
            
    bm.faces.ensure_lookup_table()
    bm.verts.index_update()
            
    # Make UVs
    if len(uv) > 0:
        uv_layer = bm.loops.layers.uv.verify()
        bm.faces.layers.tex.verify()
        
        for f in bm.faces:
            for l in f.loops:
                luv = l[uv_layer]
                luv.uv = uv[l.vert.index]

    mesh = bpy.data.meshes.new(name)

    bm.to_mesh(mesh)
    bm.free()

    return mesh

def SpeckleMesh_to_MeshObject(json, scale=1.0):
    verts, faces, uv = SpeckleMesh_to_Lists(json)
    mesh = Lists_to_Mesh(verts, faces, uv, json['geometryHash'], scale)

    obj = bpy.data.objects.new(json['name'], mesh)
    obj.speckle.object_id = json['_id']
    obj.speckle.enabled = True

        # Add material if there is one
    if 'material' in json['properties']:
        material_name = json['properties']['material']['name']
        SPrint ("Found material: %s" % material_name)
        mat = bpy.data.materials.get(material_name)

        if mat is None:
            mat = bpy.data.materials.new(name=material_name)
        obj.data.materials.append(mat)

    return obj

def MeshObject_to_SpeckleMesh(obj, scale=1.0):
    verts = [x.co * scale for x in obj.data.vertices]
    faces = [x.vertices for x in obj.data.polygons]

    sm = SpeckleMesh()
    sm.from_Lists(verts, faces)
    sm._id = obj.speckle.object_id
    sm.hash = obj.name
    sm.geometryHash = str(obj.__hash__)

    return sm

def Blender_to_Speckle(obj, scale=1.0):
    if obj.type == 'MESH':
        return MeshObject_to_SpeckleMesh(obj, scale)
    elif obj.type == 'CURVE':
        print ("This is a curve.")
    else:
        print ("Non-supported object type.")
    return None

def Speckle_to_Blender(sobj, scale=1.0):
    if sobj.type == 'Mesh':
        return SpeckleMesh_to_MeshObject(sobj, scale)
    return None

def UpdateObject(client, obj):
    if obj.speckle.enabled:
        if obj.speckle.send_or_receive == 'send':
            sobj = Blender_to_Speckle(obj, 1 / bpy.context.scene.speckle.scale)
            if sobj is not None:
                print ("Updating remote object...")
                client.UpdateObject(sobj)
        elif obj.speckle.send_or_receive == 'receive':
            sobj = client.GetObject(obj.speckle.object_id)
            if sobj is not None:
                print ("Updating local object... ")
                verts, faces, uv = SpeckleMesh_to_Lists(sobj['resource'])
                name = obj.data.name
                obj.data.name = "x" + obj.data.name
                mesh = Lists_to_Mesh(verts, faces, uv, name, bpy.context.scene.speckle.scale)
                print (mesh)
                obj.data = mesh
            else:
                print ("Failed to update object.")

