import bpy
from bpy.props import StringProperty, BoolProperty, FloatProperty, CollectionProperty, EnumProperty

#from speckle import SpeckleAddon

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
        col.operator("scene.speckle_select_stream", text='Select stream')
        col.operator("scene.speckle_select_orphans", text='Select orphans')
        col.operator("scene.speckle_not_implemented", text='Create stream')
        col.label("View")
        col.operator("scene.speckle_view_stream_data_api", text='View stream data (API)')
        col.operator("scene.speckle_view_stream_objects_api", text='View stream objects (API)')
        col.label("Admin")
        col.operator("scene.speckle_not_implemented", text='Login')
        col.operator("scene.speckle_not_implemented", text='Create profile')
        col.label("Current user:")
        col.label(context.scene.speckle.user)
