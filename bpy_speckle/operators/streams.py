'''
Stream operators
'''

import bpy, bmesh,os
import webbrowser
from bpy.props import StringProperty, BoolProperty, FloatProperty, CollectionProperty, EnumProperty

# from speckle import SpeckleApiClient
from bpy_speckle.functions import _check_speckle_client_account_stream, _get_stream_objects, _create_stream, _delete_stream, get_scale_length, _report
from bpy_speckle.convert import to_speckle_object, get_speckle_subobjects
from bpy_speckle.convert.to_speckle import export_ngons_as_polylines

from bpy_speckle.convert import from_speckle_object

from speckle.resources.streams import Stream

'''
Load stream objects
'''
class DownloadStreamObjects(bpy.types.Operator):
    bl_idname = "speckle.download_stream_objects"
    bl_label = "Download Stream Objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.context.view_layer.objects.active = None

        check = _check_speckle_client_account_stream(context.scene)
        if check is None: return {'CANCELLED'}

        client, account, stream = check        
        objects = _get_stream_objects(client, account, stream)

        if objects is None or len(objects) < 1: return {'CANCELLED'}

        '''
        Create or get Collection for stream objects
        '''

        name = "SpeckleStream_{}_{}".format(stream.name, stream.streamId)

        clear_collection = True

        if name in bpy.data.collections:
            col = bpy.data.collections[name]
            if clear_collection:
                for obj in col.objects:
                    col.objects.unlink(obj)
        else:
            #print("DEBUG: Creating new collection...")
            col = bpy.data.collections.new(name)

        existing = {}
        for obj in col.objects:
            if obj.speckle.object_id != "":
                existing[obj.speckle.object_id] = obj

        col.speckle.stream_id = stream.streamId
        col.speckle.name = stream.name
        col.speckle.units = stream.units

        '''
        Set conversion scale from stream units
        '''
        scale = get_scale_length(stream.units.lower()) / context.scene.unit_settings.scale_length 


        '''
        Get script from text editor for injection
        '''
        func = None 
        if context.scene.speckle.download_script in bpy.data.texts:
            mod = bpy.data.texts[context.scene.speckle.download_script].as_module()
            if hasattr(mod, "execute"):
                func = mod.execute

        '''
        Iterate through retrieved resources
        '''
        for obj in objects:
            new_objects = [from_speckle_object(obj, scale)]
            
            if hasattr(obj, "properties") and obj.properties is not None:
                new_objects.extend(get_speckle_subobjects(obj.properties, scale, obj.id))
            elif isinstance(obj, dict) and "properties" in obj.keys():
                new_objects.extend(get_speckle_subobjects(obj["properties"], scale, obj["id"]))

            '''
            Set object Speckle settings
            '''
            for new_object in new_objects:

                if new_object is None:
                    continue

                '''
                Run injected function
                '''
                if func:
                    new_object = func(context.scene, new_object)

                if new_object is None: # Make sure that the injected function returned an object
                    continue

                new_object.speckle.stream_id = stream.streamId
                new_object.speckle.send_or_receive = 'receive'

                if new_object.speckle.object_id in existing.keys():
                    name = existing[new_object.speckle.object_id].name
                    existing[new_object.speckle.object_id].name = name + "__deleted"
                    new_object.name = name
                    col.objects.unlink(existing[new_object.speckle.object_id])

                if new_object.name not in col.objects:
                    col.objects.link(new_object)

        if col.name not in bpy.context.scene.collection.children:
            bpy.context.scene.collection.children.link(col)

        bpy.context.view_layer.update()

        if context.area:
            context.area.tag_redraw()
        return {'FINISHED'}

class UploadStreamObjects(bpy.types.Operator):
    bl_idname = "speckle.upload_stream_objects"
    bl_label = "Upload Stream Objects"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):

        selected = context.selected_objects

        if len(selected) > 0:
            # If active object is mesh

            client = context.scene.speckle.client
            client.verbose = True
            account = context.scene.speckle.accounts[context.scene.speckle.active_account]
            stream =account.streams[account.active_stream]

            client.server = account.server
            client.s.headers.update({
                'content-type': 'application/json',
                'Authorization': account.authToken,
            })            

            scale = context.scene.unit_settings.scale_length / get_scale_length(stream.units.lower())

            placeholders = []

            '''
            Get script from text editor for injection
            '''
            func = None 
            if context.scene.speckle.upload_script in bpy.data.texts:
                mod = bpy.data.texts[context.scene.speckle.upload_script].as_module()
                if hasattr(mod, "execute"):
                    func = mod.execute

            for obj in selected:

                if obj.type != 'MESH':
                    continue

                new_object = obj
                '''
                Run injected function
                '''
                if func:
                    new_object = func(context.scene, obj)

                    if new_object is None: # Make sure that the injected function returned an object
                        continue

                _report("Converting {}".format(obj.name))

                create_objects = []

                ngons = obj.get("speckle_ngons_as_polylines", False)

                if ngons:
                    create_objects = export_ngons_as_polylines(obj, scale)
                else:
                    create_objects = [to_speckle_object(obj, scale)]

                for co in create_objects:

                    placeholder = client.objects.create(co)

                    if placeholder == None or len(placeholder) < 1: return {'CANCELLED'}

                    placeholders.extend(placeholder)

                    obj.speckle.enabled = True
                    obj.speckle.object_id = placeholder[0].id
                    obj.speckle.stream_id = stream.streamId
                    obj.speckle.send_or_receive = 'send'      

            sstream = client.streams.get(stream.streamId)
            if sstream is None: return {'CANCELLED'}

            stream_patch = Stream()

            stream_patch.objects = placeholders
            stream_patch.layers = sstream.layers
            stream_patch.baseProperties.units = stream.units
            stream_patch.commitMessage = "Modified from Blender (blender.org)."

            stream_patch.layers[-1].objectCount = len(placeholders)
            stream_patch.layers[-1].topology = "0-{}".format(len(placeholders))

            _report("Updating stream %s" % stream['streamId'])
            res = client.streams.update(stream['streamId'], stream_patch)

            _report(res)

            # Update view layer
            context.view_layer.update()

        if context.area:
            context.area.tag_redraw()
        return {'FINISHED'}

class ViewStreamDataApi(bpy.types.Operator):
    bl_idname = "speckle.view_stream_data_api"
    bl_label = "View Stream Data (API)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        if len(context.scene.speckle.accounts) > 0:
            account = context.scene.speckle.accounts[context.scene.speckle.active_account]
            if len(account.streams) > 0:
                stream =account.streams[account.active_stream]         

                webbrowser.open('%s/streams/%s' % (account.server, stream.streamId), new=2)
                return {'FINISHED'}
        return {'CANCELLED'}

class ViewStreamObjectsApi(bpy.types.Operator):
    bl_idname = "speckle.view_stream_objects_api"
    bl_label = "View Stream Objects (API)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        speckle = context.scene.speckle

        if len(speckle.accounts) > 0 and speckle.active_account >= 0 and speckle.active_account < len(speckle.accounts):
            account = speckle.accounts[speckle.active_account]

            if len(account.streams) > 0 and account.active_stream >= 0 and account.active_stream < len(account.streams):
                stream =account.streams[account.active_stream]         

                webbrowser.open('%s/streams/%s/objects?omit=displayValue,base64' % (account.server, stream.streamId), new=2)
                return {'FINISHED'}

        return {'CANCELLED'}

class CreateStream(bpy.types.Operator):
    bl_idname = "speckle.create_stream"
    bl_label = "Create Stream"
    bl_options = {'REGISTER', 'UNDO'}


    stream_name: StringProperty(
        name="Stream name",
        default="SpeckleStream")

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(self, "stream_name")
        
    def invoke(self, context, event):
        wm = context.window_manager
        if len(context.scene.speckle.accounts) > 0:
            return wm.invoke_props_dialog(self)   

        return {'CANCELLED'} 

    def execute(self, context):

        client = context.scene.speckle.client
        speckle = context.scene.speckle

        if len(speckle.accounts) > 0 and speckle.active_account >= 0 and speckle.active_account < len(speckle.accounts):
            account = speckle.accounts[speckle.active_account]

            _create_stream(client, account, self.stream_name, context.scene.unit_settings.length_unit.title())

            bpy.ops.speckle.load_account_streams()

            account.active_stream = account.streams.find(self.stream_name)

            return {'FINISHED'}

        return {'CANCELLED'}

class DeleteStream(bpy.types.Operator):
    bl_idname = "speckle.delete_stream"
    bl_label = "Delete Stream"
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

        speckle = context.scene.speckle

        check = _check_speckle_client_account_stream(context.scene)
        if check is None: return {'CANCELLED'}

        client, account, stream = check 

        _delete_stream(client, account, stream) 

        if self.delete_collection:
            col_name = "SpeckleStream_{}_{}".format(stream.name, stream.streamId)
            if col_name in bpy.data.collections:
                collection = bpy.data.collections[col_name]
                bpy.data.collections.remove(collection)

        bpy.ops.speckle.load_account_streams()

        return {'FINISHED'}

        # profiles = context.scene.speckle_client.load_local_profiles()
        # if len(profiles) < 1: raise ValueError('No profiles found.')
        # context.scene.speckle_client.use_existing_profile(sorted(profiles.keys())[0])
        # context.scene.speckle.user = sorted(profiles.keys())[0]

        # stream_ids = GetAvailableStreams(context.scene.speckle_client)
        # context.scene['speckle_streams'] = stream_ids

class SelectOrphanObjects(bpy.types.Operator):
    bl_idname = "speckle.select_orphans"
    bl_label = "Select Orphaned Objects"
    bl_options = {'REGISTER', 'UNDO'}

    def draw(self, context):
        layout = self.layout 

    def execute(self, context):

        # [o.select = True for o in context.scene.objects if o.speckle.stream_id and o.speckle.stream_id not in context.scene["speckle_streams"]]

        for o in context.scene.objects:
            if o.speckle.stream_id and o.speckle.stream_id not in context.scene['speckle_streams']:
                o.select = True
            else:
                o.select = False

        return {'FINISHED'}                  

'''
Deprecated functions
'''

class UpdateGlobal(bpy.types.Operator):
    bl_idname = "speckle.update_global"
    bl_label = "Update Global"
    bl_options = {'REGISTER', 'UNDO'}

    client = None

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        label = row.label(text="Update everything.")

    def execute(self, context):

        client = context.scene.speckle.client

        profiles = client.load_local_profiles()
        if len(profiles) < 1: raise ValueError('No profiles found.')
        client.use_existing_profile(sorted(profiles.keys())[0])
        context.scene.speckle.user = sorted(profiles.keys())[0]

        for obj in context.scene.objects:
            if obj.speckle.enabled:
                UpdateObject(context.scene.speckle_client, obj)

        context.scene.update()
        return {'FINISHED'}

