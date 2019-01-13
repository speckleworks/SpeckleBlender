import bpy
from bpy.props import StringProperty, BoolProperty, FloatProperty, CollectionProperty, EnumProperty

class SpeckleSceneObject(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(default="")

class SpeckleStreamObject(bpy.types.PropertyGroup):
    name = StringProperty(default="SpeckleStream")
    streamId = StringProperty(default="")

class SpeckleUserAccountObject(bpy.types.PropertyGroup):
    name = StringProperty(default="SpeckleUser")
    email = StringProperty(default="John Doe")
    authToken = StringProperty(default="")
    server = StringProperty(default="")
    streams = CollectionProperty(type=SpeckleStreamObject)

class SpeckleSceneSettings(bpy.types.PropertyGroup):
    streams = bpy.props.EnumProperty(
        name="Available streams",
        description="Available streams associated with account.",
        items=[],
        )

    accounts = CollectionProperty(type=SpeckleUserAccountObject)
    objects = CollectionProperty(type=SpeckleSceneObject)
    scale = FloatProperty(default=0.001)
    user = StringProperty(
    	name="User",
    	description="Current user.",
    	default="Speckle User",
    	)
