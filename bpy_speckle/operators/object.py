'''
Object operators
'''

import bpy, bmesh,os
from bpy.props import StringProperty, BoolProperty, FloatProperty, CollectionProperty, EnumProperty

from speckle import SpeckleApiClient
from bpy_speckle.convert import to_speckle_object
from bpy_speckle.convert.to_speckle import export_ngons_as_polylines

from bpy_speckle.functions import get_scale_length, _report

'''
Update local (receive) or remote (send) object depending on
the update direction. If sending, updates the object on the 
server in-place.
'''
class UpdateObject(bpy.types.Operator):
    bl_idname = "speckle.update_object"
    bl_label = "Update Object"
    bl_options = {'REGISTER', 'UNDO'}

    client = None

    def execute(self, context):
        client = context.scene.speckle.client
        account = context.scene.speckle.accounts[context.scene.speckle.active_account]
        stream = account.streams[account.active_stream]

        client.server = account.server
        client.s.headers.update({'Authorization': account.authToken})   
        
        active = context.active_object
        _report(active)

        if active is not None:
            if active.speckle.enabled:
                if active.speckle.send_or_receive == "send" and active.speckle.stream_id:
                    sstream = client.streams.get(active.speckle.stream_id)
                    #res = client.StreamGetAsync(active.speckle.stream_id)['resource']
                    #res = client.streams.get(active.speckle.stream_id)

                    if sstream is None:
                        _report ("Getting stream failed.")
                        return {'CANCELLED'}

                    stream_units = "Meters"
                    if sstream.baseProperties:
                        stream_units = sstream.baseProperties.units

                    scale = context.scene.unit_settings.scale_length / get_scale_length(stream_units)

                    sm = to_speckle_object(active, scale)

                    _report("Updating object {}".format(sm['_id']))
                    client.objects.update(active.speckle.object_id, sm)

                    return {'FINISHED'}

                    # res = client.ObjectCreateAsync([sm])
                    # new_id = res['resources'][0]['_id']

                    # for o in stream_data['objects']:
                    #     if o['_id'] == active.speckle.object_id:
                    #         o['_id'] = new_id
                    #         break

                    # res = client.StreamUpdateAsync(active.speckle.stream_id, {'objects': stream_data['objects']})
                    # res = client.ObjectDeleteAsync(active.speckle.object_id)
                    # active.speckle.object_id = new_id

                    # if res == None: return {'CANCELLED'}
            return {'FINISHED'}
        return {'CANCELLED'}            

'''
Reset Speckle object settings
'''

class ResetObject(bpy.types.Operator):
    bl_idname = "speckle.reset_object"
    bl_label = "Reset Object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        context.object.speckle.send_or_receive = "send"
        context.object.speckle.stream_id = ""
        context.object.speckle.object_id = ""
        context.object.speckle.enabled = False
        context.view_layer.update()

        return {'FINISHED'}

'''
Delete object from the server and update relevant stream
'''
class DeleteObject(bpy.types.Operator):
    bl_idname = "speckle.delete_object"
    bl_label = "Delete Object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        client = context.scene.speckle.client
        active = context.object
        if active.speckle.enabled:
            res = client.StreamGetAsync(active.speckle.stream_id)
            existing = [x for x in res['resource']['objects'] if x['_id'] == active.speckle.object_id]
            if existing == None:
                return {'CANCELLED'}
            #print("Existing: %s" % SpeckleResource.to_json_pretty(existing))
            new_objects = [x for x in res['resource']['objects'] if x['_id'] != active.speckle.object_id]
            #print (SpeckleResource.to_json_pretty(new_objects))

            res = client.GetLayers(active.speckle.stream_id)
            new_layers = res['resource']['layers']
            new_layers[-1]['objectCount'] = new_layers[-1]['objectCount'] - 1
            new_layers[-1]['topology'] = "0-%s" % new_layers[-1]['objectCount']

            res = client.StreamUpdateAsync({"objects":new_objects, "layers":new_layers}, active.speckle.stream_id)
            res = client.ObjectDeleteAsync(active.speckle.object_id)

            active.speckle.send_or_receive = "send"
            active.speckle.stream_id = ""
            active.speckle.object_id = ""
            active.speckle.enabled = False
            context.view_layer.update()

        return {'FINISHED'}

'''
Upload mesh ngon faces as polyline outlines
'''
class UploadNgonsAsPolylines(bpy.types.Operator):
    bl_idname = "speckle.upload_ngons_as_polylines"
    bl_label = "Upload Ngons As Polylines"
    bl_options = {'REGISTER', 'UNDO'}

    clear_stream: BoolProperty(
        name="Clear stream", 
        default=False,
        )


    def execute(self, context):

        active = context.active_object
        if active is not None and active.type == 'MESH':
            # If active object is mesh


            client = context.scene.speckle.client
            client.verbose = True
            account = context.scene.speckle.accounts[context.scene.speckle.active_account]
            stream = account.streams[account.active_stream]

            client.server = account.server
            client.s.headers.update({
                'content-type': 'application/json',
                'Authorization': account.authToken,
            })            

            scale = context.scene.unit_settings.scale_length / get_scale_length(stream.units)

            sp = export_ngons_as_polylines(active, scale)

            if sp is None:
                return {'CANCELLED'}

            placeholders = []
            for polyline in sp:

                #res = client.objects.create(polyline)[0]
                res = client.objects.create([polyline])
                #res = client.ObjectCreateAsync([polyline])['resources'][0]
                print(res)

                if res == None: 
                    _report(client.me)
                    continue
                placeholders.extend(res)

                #polyline['_id'] = res['_id']
                #placeholders.append({'type':'Placeholder', '_id':res['_id']})

            if len(placeholders) < 1:
                return {'CANCELLED'}

                # Get list of existing objects in stream and append new object to list
            _report("Fetching stream...")
            sstream = client.streams.get(stream.streamId)

            #res = client.StreamGetAsync(stream.streamId)
            #if res is None: return {'CANCELLED'}

            #stream = res['resource']
            #if '_id' in stream.keys():
            #    del stream['_id']

            if self.clear_stream:
                _report("Clearing stream...")
                sstream.objects = placeholders
                N = 0
            else:
                sstream.objects.extend(placeholders)

            N = sstream.layers[-1].objectCount
            if self.clear_stream:
                N = 0
            sstream.layers[-1].objectCount = N + len(placeholders)
            sstream.layers[-1].topology = "0-%s" % (N + len(placeholders))

            res = client.streams.update(sstream.streamId, sstream)

            #res = client.StreamUpdateAsync(stream['streamId'], {'objects':stream['objects'], 'layers':stream['layers']})

            # Update view layer
            context.view_layer.update()
            _report("Done.")

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)   

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "clear_stream")

class UploadObject(bpy.types.Operator):
    bl_idname = "speckle.upload_object"
    bl_label = "Upload Object"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):

        active = context.active_object
        if active is not None:
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

            _report("authToken: ", account.authToken)

            scale = context.scene.unit_settings.scale_length / get_scale_length(stream.units)

            sm = to_speckle_object(active, scale)

            #if '_id' in sm.keys():
            #    del sm['_id']

            #if 'transform' in sm.keys():
            #    del sm['transform']

            #if 'properties' in sm.keys():
            #    del sm['properties']

            placeholders = client.objects.create([sm])
            if placeholders == None: return {'CANCELLED'}

            sstream = client.streams.get(stream.streamId)
            sstream.objects.extend(placeholders)

            N = sstream.layers[-1].objectCount
            sstream.layers[-1].objectCount = N + 1
            sstream.layers[-1].topology = "0-%s" % (N + 1)

            _report("Updating stream %s" % stream['streamId'])

            res = client.streams.update(stream['streamId'], sstream)

            _report(res)

            active.speckle.enabled = True
            active.speckle.object_id = sm['_id']
            active.speckle.stream_id = stream['streamId']
            active.speckle.send_or_receive = 'send'

            # Update view layer
            context.view_layer.update()
            _report("Done.")

        return {'FINISHED'}    
     

def get_custom_speckle_props(self, context):
    ignore = ['speckle', 'cycles', 'cycles_visibility']

    active = context.active_object
    if not active: return []

    return [(x, "{}".format(x), "") for x in active.keys()]

'''
Select scene objects if they have the same custom property
value as the active object
'''

class SelectIfSameCustomProperty(bpy.types.Operator):
    bl_idname = "speckle.select_if_same_custom_props"
    bl_label = "Select Identical Custom Props"
    bl_options = {'REGISTER', 'UNDO'}

    custom_prop: EnumProperty(
        name="Custom properties",
        description="Available streams associated with account.",
        items=get_custom_speckle_props,
        )

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(self, "custom_prop")
        
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)   

    def execute(self, context):

        active = context.active_object
        if not active: 
            return {'CANCELLED'}

        if self.custom_prop not in active.keys():
            return {'CANCELLED'}

        value = active[self.custom_prop]

        _report("Looking for '{}' property with a value of '{}'.".format(self.custom_prop, value))

        for obj in bpy.data.objects:

            if self.custom_prop in obj.keys() and obj[self.custom_prop] == value:
                obj.select_set(True)
            else:
                obj.select_set(False)

        return {'FINISHED'}

'''
Select scene objects if they have the same custom property
as the active object, regardless of the value
'''

class SelectIfHasCustomProperty(bpy.types.Operator):
    bl_idname = "speckle.select_if_has_custom_props"
    bl_label = "Select Same Custom Prop"
    bl_options = {'REGISTER', 'UNDO'}

    custom_prop: EnumProperty(
        name="Custom properties",
        description="Available streams associated with account.",
        items=get_custom_speckle_props,
        )

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(self, "custom_prop")
        
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)   

    def execute(self, context):

        active = context.active_object
        if not active: 
            return {'CANCELLED'}

        if self.custom_prop not in active.keys():
            return {'CANCELLED'}

        value = active[self.custom_prop]

        _report("Looking for '{}' property.".format(self.custom_prop))

        for obj in bpy.data.objects:

            if self.custom_prop in obj.keys():
                obj.select_set(True)
            else:
                obj.select_set(False)

        return {'FINISHED'}




