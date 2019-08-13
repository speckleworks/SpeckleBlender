import bpy, bmesh,os
import webbrowser
from bpy.props import StringProperty, BoolProperty, FloatProperty, CollectionProperty, EnumProperty

from speckle import SpeckleApiClient

#from bpy_speckle.operators import get_available_streams, initialize_speckle_client

class SpeckleViewStreamDataApi(bpy.types.Operator):
    bl_idname = "scene.speckle_view_stream_data_api"
    bl_label = "Speckle - View Stream Data (API)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        if len(context.scene.speckle.accounts) > 0:
            account = context.scene.speckle.accounts[context.scene.speckle.active_account]
            if len(account.streams) > 0:
                stream =account.streams[account.active_stream]         

                webbrowser.open('%s/streams/%s' % (account.server, stream.streamId), new=2)
                return {'FINISHED'}
        return {'CANCELLED'}

class SpeckleViewStreamObjectsApi(bpy.types.Operator):
    bl_idname = "scene.speckle_view_stream_objects_api"
    bl_label = "Speckle - View Stream Objects (API)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if len(context.scene.speckle.accounts) > 0:
            account = context.scene.speckle.accounts[context.scene.speckle.active_account]
            if len(account.streams) > 0:
                stream =account.streams[account.active_stream]         

                webbrowser.open('%s/streams/%s/objects?omit=displayValue,base64' % (account.server, stream.streamId), new=2)
                return {'FINISHED'}
        return {'CANCELLED'}

class SpeckleDeleteStream(bpy.types.Operator):
    bl_idname = "scene.speckle_delete_stream"
    bl_label = "Speckle - Delete Stream"
    bl_options = {'REGISTER', 'UNDO'}

    are_you_sure: BoolProperty(
        name="Confirm",
        default=False,
        )

    delete_collection: BoolProperty(
        name="Delete collection",
        default=False)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(self, "are_you_sure")
        col.prop(self, "delete_collection")
        
    def invoke(self, context, event):
        wm = context.window_manager
        if len(context.scene.speckle.accounts) > 0:
            return wm.invoke_props_dialog(self)   


        return {'CANCELLED'} 

    def execute(self, context):
        if not self.are_you_sure:
            return {'CANCELLED'}
        self.are_you_sure = False

        if len(context.scene.speckle.accounts) > 0:
            account = context.scene.speckle.accounts[context.scene.speckle.active_account]

            client = context.scene.speckle_client
            client.server = account.server
            client.s.headers.update({'Authorization': account.authToken})

            if len(account.streams) > 0:
                stream = account.streams[account.active_stream]
                res = context.scene.speckle_client.StreamDeleteAsync(stream.streamId)
                print(res['message'])

                if self.delete_collection:
                    col_name = "SpeckleStream_{}_{}".format(stream.name, stream.streamId)
                    if col_name in bpy.data.collections:
                        collection = bpy.data.collections[col_name]
                        bpy.data.collections.remove(collection)

                bpy.ops.scene.speckle_load_account_streams()

                return {'FINISHED'}
        return {'CANCELLED'}

        profiles = context.scene.speckle_client.load_local_profiles()
        if len(profiles) < 1: raise ValueError('No profiles found.')
        context.scene.speckle_client.use_existing_profile(sorted(profiles.keys())[0])
        context.scene.speckle.user = sorted(profiles.keys())[0]

        stream_ids = GetAvailableStreams(context.scene.speckle_client)
        context.scene['speckle_streams'] = stream_ids

class SpeckleSelectOrphanObjects(bpy.types.Operator):
    bl_idname = "scene.speckle_select_orphans"
    bl_label = "Speckle - Select Orphaned Objects"
    bl_options = {'REGISTER', 'UNDO'}

    def draw(self, context):
        layout = self.layout 

    def execute(self, context):

        profiles = context.scene.speckle_client.load_local_profiles()
        if len(profiles) < 1: raise ValueError('No profiles found.')

        context.scene.speckle_client.use_existing_profile(sorted(profiles.keys())[0])
        context.scene['speckle_streams'] = GetAvailableStreams(context.scene.speckle_client)

        for o in context.scene.objects:
            if o.speckle.stream_id and o.speckle.stream_id not in context.scene['speckle_streams']:
                o.select = True
            else:
                o.select = False

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

        profiles = context.scene.speckle_client.load_local_profiles()
        if len(profiles) < 1: raise ValueError('No profiles found.')
        context.scene.speckle_client.use_existing_profile(sorted(profiles.keys())[0])
        context.scene.speckle.user = sorted(profiles.keys())[0]

        for obj in context.scene.objects:
            if obj.speckle.enabled:
                UpdateObject(context.scene.speckle_client, obj)

        context.scene.update()
        return {'FINISHED'}

