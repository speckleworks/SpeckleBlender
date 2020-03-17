'''
Scene properties
'''

import bpy
from bpy.props import StringProperty, BoolProperty, FloatProperty, CollectionProperty, EnumProperty, IntProperty, PointerProperty
from speckle import SpeckleApiClient, SpeckleCache

class SpeckleSceneObject(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(default="")

class SpeckleStreamObject(bpy.types.PropertyGroup):
    name: StringProperty(default="SpeckleStream")
    streamId: StringProperty(default="")
    units: StringProperty(default="Meters")
    query: StringProperty(default="")


class SpeckleUserAccountObject(bpy.types.PropertyGroup):
    name: StringProperty(default="SpeckleUser")
    email: StringProperty(default="John Doe")
    authToken: StringProperty(default="")
    server: StringProperty(default="")
    streams: CollectionProperty(type=SpeckleStreamObject)
    active_stream: IntProperty(default=0)

def get_scripts(self, context):
    seq = [("<none>","<none>","<none>")]
    seq.extend([(t.name, t.name, t.name) for t in bpy.data.texts])
    return seq

class SpeckleSceneSettings(bpy.types.PropertyGroup):
    streams: EnumProperty(
        name="Available streams",
        description="Available streams associated with account.",
        items=[],
        )

    accounts: CollectionProperty(type=SpeckleUserAccountObject)
    active_account: IntProperty(default=0)
    objects: CollectionProperty(type=SpeckleSceneObject)
    scale: FloatProperty(default=0.001)
    user: StringProperty(
    	name="User",
    	description="Current user.",
    	default="Speckle User",
    	)

    download_script: EnumProperty(
        name="Download script",
        description="Script to run when downloading stream objects.",
        items=get_scripts,
        )

    upload_script: EnumProperty(
        name="Upload script",
        description="Script to run when uploading stream objects.",
        items=get_scripts,
        )