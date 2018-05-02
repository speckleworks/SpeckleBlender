import bpy, bmesh,os
from bpy.props import StringProperty, BoolProperty, FloatProperty, CollectionProperty, EnumProperty

from speckle.SpeckleBlenderConverter import SpeckleMesh_to_Lists, Lists_to_Mesh, SpeckleMesh_to_MeshObject, MeshObject_to_SpeckleMesh, UpdateObject
from speckle.SpeckleClient import SpeckleClient
from speckle.SpeckleObject import SpeckleMesh
from speckle.SpeckleClientHelper import GetAvailableStreams

def initialize_speckle_client(scene):
    if 'speckle_client' not in scene:
        scene['speckle_client'] = SpeckleClient()
        profiles = scene['speckle_client'].LoadProfiles()
        if len(profiles) < 1: raise ValueError('No profiles found.')
        self.client.UseExistingProfile(sorted(profiles.keys())[0])

def get_available_streams(self, context):
    if 'speckle_streams' in context.scene.keys():
        streams = context.scene['speckle_streams']
        if streams is not None:
            return [(x, "%s (%s)" % (streams[x], x), "") for x in streams.keys()]

class SpeckleDeleteStream(bpy.types.Operator):
    bl_idname = "scene.speckle_delete_stream"
    bl_label = "Speckle - Delete Stream"
    bl_options = {'REGISTER', 'UNDO'}

    client = None
    stream_ids = {}

    stream_id = StringProperty(
        name="Stream ID",
        description="Stream ID to import objects from.",
        )

    stream_name = StringProperty(
            name="Stream ID",
            description="Target stream to update.",
            default="",
            )

    available_streams = EnumProperty(
        name="Available streams",
        description="Available streams associated with account.",
        items=get_available_streams,
        )

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "available_streams")
        
    def invoke(self, context, event):
        wm = context.window_manager
        if self.client is None:
            self.client = SpeckleClient()

        profiles = self.client.LoadProfiles()
        if len(profiles) < 1: raise ValueError('No profiles found.')
        self.client.UseExistingProfile(sorted(profiles.keys())[0])

        stream_ids = GetAvailableStreams(self.client)
        context.scene['speckle_streams'] = stream_ids

        self.stream_id = next(iter(self.stream_ids))
        self.stream_name = self.stream_ids[self.stream_id]

        return wm.invoke_props_dialog(self)    

    def execute(self, context):

        if self.stream_id == "":
            print ("Speckle: Specify stream ID.")
            return {'FINISHED'}

        if self.client is None: 
            print ("SpeckleClient was not initialized...")
            return {'CANCELLED'}

        print ("Deleting %s..." % self.available_streams)
        res = self.client.StreamDelete(self.available_streams)
        if res is None: return {'CANCELLED'}
        return {'FINISHED'}

class SpeckleImportStream(bpy.types.Operator):
    bl_idname = "scene.speckle_import_stream"
    bl_label = "Speckle - Import Stream"
    bl_options = {'REGISTER', 'UNDO'}

    client = None

    available_streams = EnumProperty(
        name="Available streams",
        description="Available streams associated with account.",
        items=get_available_streams,
        )

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "available_streams")
        
    def invoke(self, context, event):
        wm = context.window_manager
        if self.client is None:
            self.client = SpeckleClient()

        profiles = self.client.LoadProfiles()
        if len(profiles) < 1: raise ValueError('No profiles found.')
        self.client.UseExistingProfile(sorted(profiles.keys())[0])

        stream_ids = GetAvailableStreams(self.client)
        context.scene['speckle_streams'] = stream_ids

        return wm.invoke_props_dialog(self)    

    def execute(self, context):

        if self.available_streams == "":
            print ("Speckle: Specify stream ID.")
            return {'FINISHED'}

        context.scene.objects.active = None

        if self.client is None: 
            print ("SpeckleClient was not initialized...")
            return {'CANCELLED'}

        print (self.available_streams)
        res = self.client.GetStreamObjects(None, self.available_streams)
        if res is None: return {'CANCELLED'}

        objects = res['resource']['objects']

        mult = context.scene.speckle.scale

        for obj in objects:
            if obj['type'] == "Mesh":
                o = SpeckleMesh_to_MeshObject(obj, mult)
                bpy.context.scene.objects.link(o)
            elif obj['type'] == "Placeholder":
                print("Found placeholder instead.")
                obj2 = self.client.GetObject(obj['_id'])
                if obj2['resource']['type'] == "Mesh":
                    o = SpeckleMesh_to_MeshObject(obj2['resource'])
                    o.name = obj2['resource']['name']
                    o.speckle.stream_id = self.available_streams
                    bpy.context.scene.objects.link(o)

        return {'FINISHED'}


class SpeckleUploadObject(bpy.types.Operator):
    bl_idname = "object.speckle_upload_object"
    bl_label = "Speckle - Upload Object"
    bl_options = {'REGISTER', 'UNDO'}

    available_streams = EnumProperty(
        name="Available streams",
        description="Available streams associated with account.",
        items=get_available_streams,
        )

    client = None

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "available_streams")

    def invoke(self, context, event):
        wm = context.window_manager
        if self.client is None:
            self.client = SpeckleClient()

        profiles = self.client.LoadProfiles()
        if len(profiles) < 1: raise ValueError('No profiles found.')
        self.client.UseExistingProfile(sorted(profiles.keys())[0])

        stream_ids = GetAvailableStreams(self.client)
        context.scene['speckle_streams'] = stream_ids

        return wm.invoke_props_dialog(self)         

    def execute(self, context):

        if self.available_streams == "":
            print ("Speckle: Specify stream ID.")
            return {'FINISHED'}

        if self.client is None: 
            print ("SpeckleClient was not initialized...")
            return {'CANCELLED'}            

        active = context.active_object
        if active is not None:
            # If active object is mesh
            sm = MeshObject_to_SpeckleMesh(active, 1 / context.scene.speckle.scale)

            res = self.client.ObjectCreate(sm)
            if res == None: return {'CANCELLED'}
            sm._id = res['resources'][0]['_id']

            # Get list of existing objects in stream and append new object to list
            res = self.client.GetStreamObjects(None, self.available_streams)
            if res is None: return {'CANCELLED'}
            objects = res['resource']['objects']
            objects.append(sm)

            res = self.client.AddObjects(objects, self.available_streams)

            active.speckle.enabled = True
            active.speckle.object_id = sm._id
            active.speckle.stream_id = self.available_streams
            active.speckle.send_or_receive = 'receive'

        return {'FINISHED'}


class SpeckleUpdateObject(bpy.types.Operator):
    bl_idname = "object.speckle_update"
    bl_label = "Speckle - Update Object"
    bl_options = {'REGISTER', 'UNDO'}

    client = None

    def execute(self, ctx):
        if self.client is None:
            self.client = SpeckleClient()

        profiles = self.client.LoadProfiles()
        if len(profiles) < 1: raise ValueError('No profiles found.')
        self.client.UseExistingProfile(sorted(profiles.keys())[0])

        UpdateObject(self.client, ctx.object)

        return {'FINISHED'}

class SpeckleUpdateGlobal(bpy.types.Operator):
    bl_idname = "scene.speckle_update"
    bl_label = "Speckle - Update All"
    bl_options = {'REGISTER', 'UNDO'}

    client = None

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        label = row.label(text="Update everything.")

    def execute(self, context):

        if self.client is None:
            self.client = SpeckleClient()

        profiles = self.client.LoadProfiles()
        if len(profiles) < 1: raise ValueError('No profiles found.')
        self.client.UseExistingProfile(sorted(profiles.keys())[0])
        
        for obj in context.scene.objects:
            if obj.speckle.enabled:
                UpdateObject(self.client, obj)

        return {'FINISHED'}
