'''
Cache operators
'''

import bpy
from bpy.props import BoolProperty

class ClearObjectCache(bpy.types.Operator):
    bl_idname = "speckle.cache_clear_objects"
    bl_label = "Clear Object Cache"
    bl_options = {'REGISTER', 'UNDO'}

    are_you_sure: BoolProperty(
        name="Confirm",
        default=False,
        )

    def draw(self, context):

        layout = self.layout
        col = layout.column()
        col.prop(self, "are_you_sure")
        
    def invoke(self, context, event):

        wm = context.window_manager
        if len(context.scene.speckle.accounts) > 0:
            return wm.invoke_props_dialog(self)   
        return {'CANCELLED'}

    def execute(self, context):

        if not self.are_you_sure:
            return {'CANCELLED'}

        self.are_you_sure = False    	

        if _clear_cache_objects(context.scene.speckle.cache):
            return {'FINISHED'}

        return {'CANCELLED'}


class ClearAccountCache(bpy.types.Operator):
    bl_idname = "speckle.cache_clear_accounts"
    bl_label = "Clear Accounts"
    bl_options = {'REGISTER', 'UNDO'}

    are_you_sure: BoolProperty(
        name="Confirm",
        default=False,
        )

    def draw(self, context):

        layout = self.layout
        col = layout.column()
        col.prop(self, "are_you_sure")
        
    def invoke(self, context, event):

        wm = context.window_manager
        if len(context.scene.speckle.accounts) > 0:
            return wm.invoke_props_dialog(self)   
        return {'CANCELLED'}

    def execute(self, context):

        if not self.are_you_sure:
            return {'CANCELLED'}

        self.are_you_sure = False

        if _clear_cache_accounts(context.scene.speckle.cache):
            bpy.ops.speckle.accounts_load()
            return {'FINISHED'}

        return {'CANCELLED'}


class ClearStreamCache(bpy.types.Operator):
    bl_idname = "speckle.cache_clear_streams"
    bl_label = "Clear Stream Cache"
    bl_options = {'REGISTER', 'UNDO'}

    are_you_sure: BoolProperty(
        name="Confirm",
        default=False,
        )

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(self, "are_you_sure")
        
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)   

    def execute(self, context):

        if not self.are_you_sure:
            return {'CANCELLED'}

        self.are_you_sure = False       

        if _clear_cache_stream(context.scene.speckle.cache):
            return {'FINISHED'}

        return {'CANCELLED'}