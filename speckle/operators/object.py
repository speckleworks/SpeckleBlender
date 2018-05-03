import bpy, bmesh,os
from bpy.props import StringProperty, BoolProperty, FloatProperty, CollectionProperty, EnumProperty

from speckle.SpeckleBlenderConverter import SpeckleMesh_to_Lists, Lists_to_Mesh, SpeckleMesh_to_MeshObject, MeshObject_to_SpeckleMesh, UpdateObject
from speckle.SpeckleClient import SpeckleClient
from speckle.SpeckleObject import SpeckleMesh
from speckle.SpeckleClientHelper import GetAvailableStreams
from speckle.operators import get_available_streams, initialize_speckle_client

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