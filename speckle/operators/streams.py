import bpy, bmesh,os
from bpy.props import StringProperty, BoolProperty, FloatProperty, CollectionProperty, EnumProperty

from speckle.SpeckleBlenderConverter import SpeckleMesh_to_Lists, Lists_to_Mesh, SpeckleMesh_to_MeshObject, MeshObject_to_SpeckleMesh, UpdateObject
from speckle.SpeckleClient import SpeckleClient
from speckle.SpeckleObject import SpeckleMesh
from speckle.SpeckleClientHelper import GetAvailableStreams
from speckle.operators import get_available_streams, initialize_speckle_client


class SpeckleDeleteStream(bpy.types.Operator):
    bl_idname = "scene.speckle_delete_stream"
    bl_label = "Speckle - Delete Stream"
    bl_options = {'REGISTER', 'UNDO'}

    client = None

    available_streams = EnumProperty(
        name="Available streams",
        description="Available streams associated with account.",
        items=get_available_streams,
        )

    are_you_sure = BoolProperty(
        name="Confirm",
        default=False,
        )

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(self, "available_streams")
        col.prop(self, "are_you_sure")
        
    def invoke(self, context, event):
        wm = context.window_manager
        if self.client is None:
            self.client = SpeckleClient()

        profiles = self.client.LoadProfiles()
        if len(profiles) < 1: raise ValueError('No profiles found.')
        self.client.UseExistingProfile(sorted(profiles.keys())[0])
        context.scene.speckle.user = sorted(profiles.keys())[0]

        stream_ids = GetAvailableStreams(self.client)
        context.scene['speckle_streams'] = stream_ids

        return wm.invoke_props_dialog(self)    

    def execute(self, context):
        if not self.are_you_sure:
            print ("Deleting stream %s cancelled." % self.available_streams)
            return {'CANCELLED'}

        if self.available_streams == "":
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
        context.scene.speckle.user = sorted(profiles.keys())[0]

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

        for obj in objects:
            if obj['type'] == "Mesh":
                o = SpeckleMesh_to_MeshObject(obj, context.scene.speckle.scale)
                bpy.context.scene.objects.link(o)
            elif obj['type'] == "Placeholder":
                obj2 = self.client.GetObject(obj['_id'])
                if obj2['resource']['type'] == "Mesh":
                    o = SpeckleMesh_to_MeshObject(obj2['resource'], context.scene.speckle.scale)
                    o.name = obj2['resource']['name']
                    o.speckle.stream_id = self.available_streams
                    o.speckle.send_or_receive = 'receive'
                    o.select = True
                    bpy.context.scene.objects.link(o)

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
        context.scene.speckle.user = sorted(profiles.keys())[0]

        for obj in context.scene.objects:
            if obj.speckle.enabled:
                UpdateObject(self.client, obj)

        return {'FINISHED'}


class NotImplementedOperator(bpy.types.Operator):
    bl_idname = "scene.speckle_not_implemented"
    bl_label = "Speckle - Dummy"
    bl_options = {'REGISTER', 'UNDO'}

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        label = row.label(text="Not implemented.")

    def execute(self, context):

        print ("Speckle :: Not implemented.")

        return {'FINISHED'}