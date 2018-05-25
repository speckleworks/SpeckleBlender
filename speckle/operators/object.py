import bpy, bmesh,os
from bpy.props import StringProperty, BoolProperty, FloatProperty, CollectionProperty, EnumProperty

from speckle.SpeckleBlenderConverter import SpeckleMesh_to_Lists, Lists_to_Mesh, SpeckleMesh_to_MeshObject, MeshObject_to_SpeckleMesh, UpdateObject
from speckle.api.SpeckleClient import SpeckleClient, SpeckleResource
from speckle.api.SpeckleLayer import SpeckleLayer
from speckle.api.SpeckleStream import SpeckleStream
from speckle.SpeckleClientHelper import GetAvailableStreams
from speckle.operators import get_available_streams, initialize_speckle_client

class SpeckleUpdateObject(bpy.types.Operator):
    bl_idname = "object.speckle_update"
    bl_label = "Speckle - Update Object"
    bl_options = {'REGISTER', 'UNDO'}

    client = None

    def execute(self, context):
        profiles = context.scene.speckle_client.LoadProfiles()
        if len(profiles) < 1: raise ValueError('No profiles found.')
        context.scene.speckle_client.UseExistingProfile(sorted(profiles.keys())[0])

        UpdateObject(context.scene.speckle_client, context.object)

        return {'FINISHED'}

class SpeckleResetObject(bpy.types.Operator):
    bl_idname = "object.speckle_reset"
    bl_label = "Speckle - Reset Object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        
        context.object.speckle.send_or_receive = "send"
        context.object.speckle.stream_id = ""
        context.object.speckle.object_id = ""
        context.object.speckle.enabled = False

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

        profiles = context.scene.speckle_client.LoadProfiles()
        if len(profiles) < 1: raise ValueError('No profiles found.')
        context.scene.speckle_client.UseExistingProfile(sorted(profiles.keys())[0])

        stream_ids = GetAvailableStreams(context.scene.speckle_client)
        context.scene['speckle_streams'] = stream_ids

        return wm.invoke_props_dialog(self)         

    def execute(self, context):

        if self.available_streams == "":
            print ("Speckle: Specify stream ID.")
            return {'FINISHED'}         

        active = context.active_object
        if active is not None:
            # If active object is mesh
            sm = MeshObject_to_SpeckleMesh(active, 1 / context.scene.speckle.scale)

            res = context.scene.speckle_client.ObjectCreate(sm)
            if res == None: return {'CANCELLED'}
            sm._id = res.resources[0]._id
            pl = SpeckleResource({'type':'Placeholder', '_id':res.resources[0]._id})

            # Get list of existing objects in stream and append new object to list
            res = context.scene.speckle_client.GetStreamObjects(self.available_streams)
            if res is None: return {'CANCELLED'}

            stream_name = res.resource.name
            objects = [x for x in res.resource.objects]
            N_current = len(objects)
            objects.append(pl)

            res = context.scene.speckle_client.GetLayers(self.available_streams)
            if res is None: return {'CANCELLED'}
            print (res)

            layers = res.resource.layers
            new_layers = []
            if layers is None or len(layers) < 1:
                layer = SpeckleLayer()
                layer.name = "Blender"
                layer.guid = ""
                layer.orderIndex = 0
                layer.startIndex = 0
                layer.objectCount = len(objects)
                layer.topology = "0-%s" % len(objects)
                new_layers.append(layer)
            else:
                new_layers = [SpeckleLayer(x) for x in layers]
                N = new_layers[-1].objectCount
                new_layers[-1].objectCount = N + 1
                new_layers[-1].topology = "0-%s" % (N + 1)

            stream = SpeckleStream()
            stream.name = stream_name
            stream.objects = objects
            stream.layers = new_layers

            res = context.scene.speckle_client.UpdateStream(stream, self.available_streams)

            #res = self.client.AddObjects(objects, self.available_streams)
            #res = self.client.UpdateLayers(new_layers, self.available_streams)

            active.speckle.enabled = True
            active.speckle.object_id = sm._id
            active.speckle.stream_id = self.available_streams
            active.speckle.send_or_receive = 'receive'

        return {'FINISHED'}        