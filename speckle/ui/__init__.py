import bpy
from bpy.props import StringProperty, BoolProperty, FloatProperty, CollectionProperty, EnumProperty

#from speckle import SpeckleAddon

#
#   OBJECT_PT_speckle(bpy.types.Panel)
#

class OBJECT_PT_speckle(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    #bl_idname = 'OBJECT_PT_speckle'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    bl_label = "Speckle"

    def draw_header(self, context):
        self.layout.prop(context.object.speckle, "enabled", text="")


    def draw(self, context):
        ob = context.object
        layout = self.layout
        layout.active = ob.speckle.enabled
        row = layout.row()
        #print (ob.speckle_settings.enabled)

        row.prop(ob.speckle, "send_or_receive", expand=True)
        row = layout.row()
        row.prop(ob.speckle, "stream_id", text="Stream ID")
        row = layout.row()
        row.prop(ob.speckle, "object_id", text="Object ID")
        row = layout.row()
        row.operator("object.speckle_update", text='Update')
        #row.prop(ob, "speckle_settings.stream_id", text="Stream ID")

#
#   SCENE_PT_speckle(bpy.types.Panel)
#

class SCENE_PT_speckle(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    #bl_idname = 'SCENE_PT_speckle'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_label = "Speckle Settings"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        label = row.label(text="Speckle global settings.")
        row = layout.row()
        row.prop(context.scene.speckle, "scale", text="Scale")
        row = layout.row()
        row.operator("scene.speckle_update", text='Update all')
        row.operator("scene.speckle_import_stream", text='Import stream')

def menu_func(self, context):
    self.layout.operator(SpeckleUpdateObject.bl_idname, icon='MESH_CUBE')

class VIEW3D_PT_speckle(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Speckle'
    bl_context = "objectmode"
    bl_label = "Speckle.Works"

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.operator("scene.speckle_update", text='Update scene')
        col.label("Streams")
        col.operator("scene.speckle_import_stream", text='Import stream')
        col.operator("scene.speckle_delete_stream", text='Delete stream')
        col.operator("scene.speckle_not_implemented", text='Create stream')
        col.label("Admin")
        col.operator("scene.speckle_not_implemented", text='Login')
        col.operator("scene.speckle_not_implemented", text='Create profile')
        col.label("Current user:")
        col.label(context.scene.speckle.user)
