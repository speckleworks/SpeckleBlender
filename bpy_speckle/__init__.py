# MIT License

# Copyright (c) 2018-2019 Nathan Letwory, Joel Putnam, Tom Svilans

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


bl_info = {
    "name": "SpeckleBlender",
    "author": "Tom Svilans",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "File > Import > SpeckleBlender",
    "description": "This addon lets you use the Speckle Python client",
    "warning": "This add-on is WIP and should be used with caution",
    "wiki_url": "https://github.com/jesterKing/import_3dm",
    "category": "Scene",
}

import bpy
# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

# Try to import PySpeckle and install if necessary using pip
try:
    import speckle
except:
    print("Failed to load PySpeckle.")
    print("Attempting to install using pip...")
    try:
        import pip
        pip.main(['install', 'speckle'])
    except:
        raise Exception("Failed to import pip. Please make sure you have pip installed.")

from speckle import SpeckleApiClient

from bpy_speckle.ui.view3d import VIEW3D_PT_speckle, VIEW3D_UL_SpeckleAccounts, VIEW3D_UL_SpeckleStreams
from bpy_speckle.properties.scene import SpeckleSceneSettings, SpeckleSceneObject, SpeckleUserAccountObject, SpeckleStreamObject
from bpy_speckle.properties.object import SpeckleObjectSettings
from bpy_speckle.operators.accounts import SpeckleLoadAccounts, SpeckleAddAccount, SpeckleImportStream2
from bpy_speckle.operators.object import SpeckleUpdateObject
from bpy_speckle.operators.streams import SpeckleViewStreamDataApi, SpeckleViewStreamObjectsApi, SpeckleDeleteStream, SpeckleSelectStream, SpeckleSelectOrphanObjects
from bpy_speckle.operators.streams import NotImplementedOperator, SpeckleImportStream, SpeckleImportStreamRaw, SpeckleUpdateGlobal


classes = [
    VIEW3D_PT_speckle, 
    VIEW3D_UL_SpeckleAccounts, 
    VIEW3D_UL_SpeckleStreams,
    SpeckleSceneObject, 
    SpeckleStreamObject,    
    SpeckleUserAccountObject,
    SpeckleSceneSettings, 
    SpeckleObjectSettings,
]

classes.extend([
    SpeckleLoadAccounts, 
    SpeckleAddAccount, 
    SpeckleImportStream2
    ])

classes.extend([
    SpeckleUpdateObject
    ])

classes.extend([
    SpeckleViewStreamDataApi, 
    SpeckleViewStreamObjectsApi, 
    SpeckleDeleteStream, 
    SpeckleSelectStream, 
    SpeckleSelectOrphanObjects, 
    SpeckleImportStream, 
    SpeckleImportStreamRaw, 
    SpeckleUpdateGlobal,
    NotImplementedOperator,
    ])

import blf

def draw_speckle_info(self, context):
    scn = bpy.context.scene
    if len(scn.speckle.accounts) > 0:
        account = scn.speckle.accounts[scn.speckle.active_account]
        dpi = bpy.context.preferences.system.dpi

        blf.position(0, 100, 50, 0)
        blf.size(0, 20, dpi)
        blf.draw(0, "Active Speckle account: {} ({})".format(account.name, account.email))
        blf.position(0, 100, 20, 0)
        blf.size(0, 16, dpi)
        blf.draw(0, "Server: {}".format(account.server))

handler = None

def register():
    
    from bpy.utils import register_class, unregister_class
    for cls in classes:
        print("class: {} class_name: {}".format(cls, cls.__name__))

        if hasattr(bpy.types, cls.__name__):
            print("   already registered")
            unregister_class(cls)
        register_class(cls)

    bpy.types.Scene.speckle = bpy.props.PointerProperty(type=SpeckleSceneSettings)

    #from . properties.object import SpeckleObjectSettings
    bpy.types.Object.speckle = bpy.props.PointerProperty(type=SpeckleObjectSettings)

    bpy.types.Scene.speckle_client = SpeckleApiClient()

    handler = bpy.types.SpaceView3D.draw_handler_add(draw_speckle_info, (None, None), 'WINDOW', 'POST_PIXEL')


def unregister():
    if handler:
        bpy.types.SpaceView3D.draw_handler_remove(handler, "WINDOW")

    from bpy.utils import unregister_class
    for cls in reversed(classes):
        if hasattr(bpy.types, cls.__name__):
            unregister_class(cls)

if __name__ == "__main__":
    unregister()
    print("\nRELOADING\n")
    register()


    #for cls in classes:
    #    if hasattr(bpy.types, cls.idname()):
    #        unregister_class(cls)
    #    register_class(cls)

    # test call
    #bpy.ops.import_3dm.some_data('INVOKE_DEFAULT')