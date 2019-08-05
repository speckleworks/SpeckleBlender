import bpy, bmesh, struct
from .object import add_custom_properties, add_material

def add_vertices(smesh, bmesh, scale=1.0):
    
    vertKey = ""
    if 'vertices' in smesh.keys():
        vertKey = 'vertices'
    elif 'Vertices' in smesh.keys():
        vertKey = 'Vertices'

    if vertKey != "":
        sverts = smesh[vertKey]
        if len(sverts) > 0:
            for i in range(0, len(sverts), 3):
                bmesh.verts.new((float(sverts[i]) * scale, float(sverts[i + 1]) * scale, float(sverts[i + 2]) * scale))  
        
    bmesh.verts.ensure_lookup_table()  

def add_faces(smesh, bmesh):
    
    faceKey = ""
    if 'faces' in smesh.keys():
        faceKey = 'faces'
    elif 'Faces' in smesh.keys():
        faceKey = 'Faces'

    if faceKey != "":
        sfaces = smesh[faceKey]
        if len(sfaces) > 0:
            i = 0
            while (i < len(sfaces)):
                if (sfaces[i] == 0):
                    i += 1
                    f = bmesh.faces.new((bmesh.verts[int(sfaces[i])], bmesh.verts[int(sfaces[i + 1])], bmesh.verts[int(sfaces[i + 2])]))
                    f.smooth = True
                    i += 3
                elif (sfaces[i] == 1):
                    i += 1
                    f = bmesh.faces.new((bmesh.verts[int(sfaces[i])], bmesh.verts[int(sfaces[i + 1])], bmesh.verts[int(sfaces[i + 2])], bmesh.verts[int(sfaces[i + 3])]))
                    f.smooth = True
                    i += 4
                else:
                    print("Invalid face length.\n" + str(sfaces[i]))
                    break   
            
            bmesh.faces.ensure_lookup_table()
            bmesh.verts.index_update()     

def add_colors(smesh, bmesh):
    colors = []

    colKey = ""
    if 'colors' in smesh.keys():
        colKey = 'colors'
    elif 'Colors' in smesh.keys():
        colKey = 'Colors'

    if colKey != "":
        scolors = smesh[colKey]
        if len(scolors) > 0:

            for i in range(0, len(scolors)):
                col = int(scolors[i])
                (a, r, g, b) = [int(x) for x in struct.unpack("!BBBB", struct.pack("!i", col))]
                colors.append((float(r) / 255.0, float(g) / 255.0, float(b) / 255.0, float(a) / 255.0)) 

        # Make vertex colors
        if len(scolors) == len(bmesh.verts):
            color_layer = bmesh.loops.layers.color.new("Col")

            for face in bmesh.faces:
                for loop in face.loops:
                    loop[color_layer] = colors[loop.vert.index]

def add_uv_coords(smesh, bmesh):

    if 'properties' in smesh.keys():
        sprops = smesh["properties"]
        if sprops is not None:
            texKey = ""
            if 'texture_coordinates' in sprops.keys():
                texKey = 'texture_coordinates'
            elif 'TextureCoordinates' in sprops.keys():
                texKey = "TextureCoordinates"

            if texKey != "":

                try:
                    decoded = base64.b64decode(sprops[texKey]).decode("utf-8")
                    s_uvs = decoded.split()
                      
                    if int(len(s_uvs) / 2) == len(bmesh.verts):
                        for i in range(0, len(s_uvs), 2):
                            uv.append((float(s_uvs[i]), float(s_uvs[i+1])))
                    else:
                        print (len(s_uvs) * 2)
                        print (len(bmesh.verts))
                        print ("Failed to match UV coordinates to vert data.")
                except:
                    pass
                '''
                if len(uv) == len(verts):
                    uv_layer = bm.loops.layers.uv.verify()
                    bm.faces.layers.tex.verify()
                    
                    for f in bm.faces:
                        for l in f.loops:
                            luv = l[uv_layer]
                            luv.uv = uv[l.vert.index]
                '''
                del smesh['properties'][texKey]


def to_bmesh(smesh, name="SpeckleMesh", scale=1.0):

    bm = bmesh.new()

    add_vertices(smesh, bm, scale)
    add_faces(smesh, bm)
    add_colors(smesh, bm)
    add_uv_coords(smesh, bm)

    if name in bpy.data.meshes.keys():
        mesh = bpy.data.meshes[name]
    else:
        mesh = bpy.data.meshes.new(name=name)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()

    return mesh


def import_mesh(speckle_mesh, scale=1.0):

    name = speckle_mesh['_id']
    mesh = to_bmesh(speckle_mesh, name, scale)

    if 'name' in speckle_mesh and speckle_mesh['name'] is not None:
        name = speckle_mesh['name']
        print("Name is: ", name)

    obj = bpy.data.objects.new(name, mesh)

    obj.speckle.object_id = speckle_mesh['_id']
    obj.speckle.enabled = True
    obj.data.use_auto_smooth = True
    #obj.data.auto_smooth_angle = 30

    add_material(speckle_mesh, obj)
    add_custom_properties(speckle_mesh, obj)

    return obj	