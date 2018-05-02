import bpy
from bpy.props import StringProperty, BoolProperty, FloatProperty, CollectionProperty, EnumProperty

class SpeckleSceneObject(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(default="")

class SpeckleSceneSettings(bpy.types.PropertyGroup):
    streams = bpy.props.EnumProperty(
        name="Available streams",
        description="Available streams associated with account.",
        items=[],
        )

    objects = bpy.props.CollectionProperty(type=SpeckleSceneObject)
    scale = bpy.props.FloatProperty(default=1.0)
