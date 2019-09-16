import bpy, bmesh,os
from bpy.props import StringProperty, BoolProperty, FloatProperty, CollectionProperty, EnumProperty
from bpy_speckle.properties.scene import SpeckleUserAccountObject

from bpy_speckle.convert import from_speckle_object
from bpy_speckle.convert import to_speckle_object

from speckle import SpeckleApiClient


def tuple_to_account(tup):
    assert len(tup) > 4

    profile = {}
    profile["server_name"] = tup[1]
    profile["server"] = tup[2]
    profile["email"] = tup[3]
    profile["apitoken"] = tup[4]

    return profile

class SpeckleLoadAccounts(bpy.types.Operator):
    bl_idname = "scene.speckle_accounts_load"
    bl_label = "Speckle - Load Accounts"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        client = context.scene.speckle_client
        context.scene.speckle.accounts.clear()

        cache = context.scene.speckle_cache
        if not cache.try_connect():
            cache.create_database()

        profiles = cache.get_all_accounts()

        # If can't find SpeckleCache.db, try MigratedAccounts
        #if len(profiles) < 1:
        #    profiles = client.load_local_profiles(None)

        for tup in profiles:
            #print(p)
            p = tuple_to_account(tup)

            ua = context.scene.speckle.accounts.add()
            ua.name = p['server_name']
            ua.server=p['server'] 
            ua.email=p['email']
            ua.authToken = p['apitoken']

            client.server = ua.server
            client.s.headers.update({
                'content-type': 'application/json',
                'Authorization': ua.authToken,
            })

            res = client.StreamsGetAllAsync()
            if res == None or res['resources'] == None:
                return {'CANCELLED'}

            streams = sorted(res['resources'], key=lambda x: x['name'], reverse=False)

            for s in streams:
                stream = ua.streams.add()
                stream.name = s['name']
                stream.streamId = s['streamId']
                if 'baseProperties' in s.keys() and s['baseProperties'] is not None:
                    #print (s['baseProperties'])
                    if 'units' in s['baseProperties'].keys():
                        stream.units = s['baseProperties']['units']

        return {'FINISHED'}


class SpeckleAddAccount(bpy.types.Operator):
    bl_idname = "scene.speckle_account_add"
    bl_label = "Speckle - Add Account"
    bl_options = {'REGISTER', 'UNDO'}

    email: StringProperty(name="Email", description="User email.", default="")
    pwd: StringProperty(name="Password", description="User password.", default="", subtype='PASSWORD')
    host: StringProperty(name="Server", description="Server address.", default="https://hestia.speckle.works/api/v1")

    def execute(self, context):

        client = context.scene.speckle_client
        client.server = self.host
        client.verbose = True

        if self.host is "":
            return {'FINISHED'}

        cache = context.scene.speckle_cache

        if not cache.try_connect():
            cache.create_database()

        if cache.account_exists(self.host, self.email):
            print("Account already in database.")
            if True:
                cache.delete_account(self.host, self.email)
            else:
                return {'CANCELLED'}

        try:
            client.login(email=self.email, password=self.pwd)
        except AssertionError as e:
            print("Login failed.")
            return {'CANCELLED'}

        #print(client.me)
        authtoken = client.me["apitoken"]

        '''
        user = {
            'email': self.email, 
            'server': self.host,
            'server_name': "SpeckleServer",
            'apitoken': client.s.headers['Authorization']}
        '''

        cache.write_account(self.host, "Speckle Hestia", self.email, authtoken)

        bpy.ops.scene.speckle_accounts_load()

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self) 

class SpeckleLoadAccountStreams(bpy.types.Operator):
    bl_idname = "scene.speckle_load_account_streams"
    bl_label = "Speckle - Load Account Streams"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        if len(context.scene.speckle.accounts) > 0 and context.scene.speckle.active_account >= 0:

            account = context.scene.speckle.accounts[context.scene.speckle.active_account]

            client = context.scene.speckle_client
            client.server = account.server
            client.s.headers.update({'Authorization': account.authToken})

            account.streams.clear()
            res = client.StreamsGetAllAsync()
            if res == None or res['resources'] == None:
                return {'CANCELLED'}

            streams = sorted(res['resources'], key=lambda x: x['name'], reverse=False)

            for s in streams:
                stream = account.streams.add()
                stream.name = s['name']
                stream.streamId = s['streamId']
                if 'baseProperties' in s.keys() and s['baseProperties'] is not None:
                    if 'units' in s['baseProperties'].keys():
                        stream.units = s['baseProperties']['units']   

            return {'FINISHED'}
        return {'CANCELLED'}

unit_scale = {
    'Meters':1.0,
    'Centimeters':0.01,
    'Millimeters':0.001,
    'Inches':0.0254,
    'Feet':0.3048,
    'Kilometers':1000.0,
}

def get_scale_length(units):
    if units in unit_scale.keys():
        return unit_scale[units]
    return 1.0

class SpeckleImportStream2(bpy.types.Operator):
    bl_idname = "scene.speckle_import_stream2"
    bl_label = "Speckle - Import Stream"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.context.view_layer.objects.active = None

        if context.scene.speckle_client is None: 
            print ("SpeckleClient was not initialized...")
            return {'CANCELLED'}

        client = context.scene.speckle_client

        if len(context.scene.speckle.accounts) < 1:
            print("No accounts loaded.")
            return {'CANCELLED'}

        account = context.scene.speckle.accounts[context.scene.speckle.active_account]

        if len(account.streams) < 1:
            print("Account contains no streams.")
            return {'CANCELLED'}

        stream = account.streams[account.active_stream]

        scale = context.scene.unit_settings.scale_length * get_scale_length(stream.units)
        
        client.server = account.server
        client.s.headers.update({'Authorization': account.authToken})

        if stream.query:
            print(stream.query)
            res = context.scene.speckle_client.StreamGetObjectsAsync(stream.streamId, stream.query)
        else:
            res = context.scene.speckle_client.StreamGetObjectsAsync(stream.streamId)
        if res is None: return {'CANCELLED'}

        name = "SpeckleStream_{}_{}".format(stream.name, stream.streamId)

        clear_collection = True

        if name in bpy.data.collections:
            col = bpy.data.collections[name]
            if clear_collection:
                for obj in col.objects:
                    col.objects.unlink(obj)
        else:
            print("DEBUG: Creating new collection...")
            col = bpy.data.collections.new(name)

        existing = {}
        for obj in col.objects:
            if obj.speckle.object_id != "":
                existing[obj.speckle.object_id] = obj

        col.speckle.stream_id = stream.streamId
        col.speckle.name = stream.name
        col.speckle.units = stream.units

        if 'resources' in res.keys():
            for resource in res['resources']:
                o = from_speckle_object(resource, scale)

                if o is None:
                    continue

                o.speckle.stream_id = stream.streamId
                o.speckle.send_or_receive = 'receive'

                if o.speckle.object_id in existing.keys():
                    name = existing[o.speckle.object_id].name
                    existing[o.speckle.object_id].name = name + "__deleted"
                    o.name = name
                    col.objects.unlink(existing[o.speckle.object_id])

                col.objects.link(o)

                #o.select_set(True)
                #bpy.context.scene.objects.link(o)

        else:
            pass

        if col.name not in bpy.context.scene.collection.children:
            bpy.context.scene.collection.children.link(col)

        bpy.context.view_layer.update()
        #print ("Received %i objects." % len(res.resources))
        return {'FINISHED'}


class SpeckleClearObjectCache(bpy.types.Operator):
    bl_idname = "scene.speckle_cache_clear_objects"
    bl_label = "SpeckleCache - Clear Object Cache"
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

        cache = context.scene.speckle_cache
        if not cache.try_connect():
            return {'CANCELLED'}

        cache.delete_all("CachedObject")

        return {'FINISHED'}


class SpeckleClearAccountCache(bpy.types.Operator):
    bl_idname = "scene.speckle_cache_clear_accounts"
    bl_label = "SpeckleCache - Clear Accounts"
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

        cache = context.scene.speckle_cache
        if not cache.try_connect():
            return {'CANCELLED'}

        cache.delete_all("Account")
        bpy.ops.scene.speckle_accounts_load()

        return {'FINISHED'}


class SpeckleClearStreamCache(bpy.types.Operator):
    bl_idname = "scene.speckle_cache_clear_streams"
    bl_label = "SpeckleCache - Clear Stream Cache"
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

        cache = context.scene.speckle_cache
        if not cache.try_connect():
            return {'CANCELLED'}

        cache.delete_all("CachedStream")

        return {'FINISHED'}   