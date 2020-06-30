'''
Speckle UI elements for the 3d viewport
'''

import bpy
from bpy.props import StringProperty, BoolProperty, FloatProperty, CollectionProperty, EnumProperty

from bpy_speckle.functions import _get_accounts, _add_account, _get_streams, _report

'''
Compatibility 
'''

if bpy.app.version < (2,80,0):
    Region = "TOOLS"
else:
    Region = "UI"

# def menu_func(self, context):
#     self.layout.operator(SpeckleUpdateObject.bl_idname, icon='MESH_CUBE')

'''
Function to populate accounts list
'''
def get_available_accounts(self, context):
    return [(a, a, a.name) for a in context.scene.speckle.accounts]

'''
Speckle account list
'''

class VIEW3D_UL_SpeckleAccounts(bpy.types.UIList):

    def draw_item(self, context, layout, data, account, active_data, active_propname):
        ob = data
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if account:
                #layout.prop(account, "name", text=account.name, emboss=False, icon_value=0)
                layout.label(text=account.name + ' (' + account.email + ')', translate=False, icon_value=0)
            else:
                layout.label(text="", translate=False, icon_value=0)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="Accounts", icon_value=0)

'''
Speckle stream list
'''

class VIEW3D_UL_SpeckleStreams(bpy.types.UIList):
    def draw_item(self, context, layout, data, stream, active_data, active_propname):
        ob = data
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if stream:
                #layout.prop(account, "name", text=account.name, emboss=False, icon_value=0)
                layout.label(text=stream.name + ' (' + stream.streamId + ')', translate=False, icon_value=0)
            else:
                layout.label(text="", translate=False, icon_value=0)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="Accounts", icon_value=0)

'''
Main Speckle UI panel in the 3d viewport
'''

class VIEW3D_PT_speckle(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_space_type = 'VIEW_3D'
    bl_region_type = Region
    bl_category = 'Speckle'
    bl_context = "objectmode"
    bl_label = "Speckle.Works"

    def draw(self, context):

        scn = context.scene
        speckle = scn.speckle


        layout = self.layout
        col = layout.column()

        col.label(text="Accounts")
        if len(speckle.accounts) > 0:
            col.label(text="Current user: %s" % speckle.accounts[speckle.active_account].name)

        col.operator("speckle.account_add", text="Add Account")
        col.operator("speckle.accounts_load", text="Load Accounts")
        col.template_list("VIEW3D_UL_SpeckleAccounts", "", speckle, "accounts", speckle, "active_account")

        col.separator()
        col.label(text="Streams")
        col.operator("speckle.load_account_streams", text="Refresh")

        if len(speckle.accounts) > 0:
            speckle.active_account = min(speckle.active_account, len(speckle.accounts) - 1)
            account = speckle.accounts[speckle.active_account]
            col.template_list("VIEW3D_UL_SpeckleStreams", "", account, "streams", account, "active_stream")
            col.separator()

            

            if len(account.streams) > 0:
                account.active_stream = min(account.active_stream, len(account.streams) - 1)

                col.prop(account.streams[account.active_stream], "query", text="Filter")
                col.operator("speckle.download_stream_objects", text="Download Objects")
                col.prop(speckle, "download_script", text="Download script")
                col.operator("speckle.upload_stream_objects", text="Upload Objects")                
                col.prop(speckle, "upload_script", text="Upload script")
                col.separator()
                col.operator("speckle.create_stream", text="Create Stream")                
                col.operator("speckle.delete_stream", text="Delete Stream")                
                col.label(text="Active stream: %s" % account.streams[account.active_stream].name)
                col.label(text="Stream ID: %s" % account.streams[account.active_stream].streamId)
                col.label(text="Units: %s" % account.streams[account.active_stream].units)
            else:
                bpy.ops.speckle.load_account_streams()


        col.separator()
        col.label(text="View")
        col.operator("speckle.view_stream_data_api", text='View stream data (API)')
        col.operator("speckle.view_stream_objects_api", text='View stream objects (API)')
        col.separator()
        col.label(text="Cache")
        col.operator("speckle.cache_clear_objects", text="Clear Object Cache")
        col.operator("speckle.cache_clear_streams", text="Clear Stream Cache")
        col.operator("speckle.cache_clear_accounts", text="Clear Accounts")

