'''
Account operators
'''

import bpy, bmesh,os
from bpy.props import StringProperty, BoolProperty, FloatProperty, CollectionProperty, EnumProperty
from bpy_speckle.properties.scene import SpeckleUserAccountObject

from bpy_speckle.convert import from_speckle_object, get_speckle_subobjects
from bpy_speckle.convert import to_speckle_object

from bpy_speckle.functions import _get_accounts, _add_account, _get_streams, _report

from speckle import SpeckleApiClient

'''
Add user account to local user database,
login, and populate stream list with available
streams
'''
class AddAccount(bpy.types.Operator):
    bl_idname = "speckle.account_add"
    bl_label = "Add Account"
    bl_options = {'REGISTER', 'UNDO'}

    email: StringProperty(name="Email", description="User email.", default="")
    pwd: StringProperty(name="Password", description="User password.", default="", subtype='PASSWORD')
    host: StringProperty(name="Server", description="Server address.", default="https://hestia.speckle.works/api/v1")

    def execute(self, context):

        client = context.scene.speckle.client
        cache = context.scene.speckle.cache

        if self.host is "":
            return {'CANCELLED'}

        _add_account(client, cache, self.email, self.pwd, self.host, "Speckle Hestia")

        bpy.ops.speckle.accounts_load()

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self) 

'''
Load all accounts from local user database
'''
class LoadAccounts(bpy.types.Operator):
    bl_idname = "speckle.accounts_load"
    bl_label = "Load Accounts"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        speckle = context.scene.speckle
        client = speckle.client

        _report("Loading accounts...")

        _get_accounts(context.scene)
        bpy.context.view_layer.update()

        # for account in speckle.accounts:
            # _get_streams(client, account)

        if context.area:
            context.area.tag_redraw()
        return {'FINISHED'}

'''
Load all available streams for active user account
'''
class LoadAccountStreams(bpy.types.Operator):
    bl_idname = "speckle.load_account_streams"
    bl_label = "Load Account Streams"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        speckle = context.scene.speckle
        client = context.scene.speckle.client

        if len(speckle.accounts) > 0 and speckle.active_account >= 0 and speckle.active_account < len(speckle.accounts):
            account = speckle.accounts[speckle.active_account]
            _get_streams(client, account, {'deleted':'false', 'omit':'objects'}, omit_clones=True)
            bpy.context.view_layer.update()

            return {'FINISHED'}

        if context.area:
            context.area.tag_redraw()
        return {'CANCELLED'}

