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

import os, sys

def modules_path():
    # set up addons/modules under the user
    # script path. Here we'll install the
    # dependencies
    modulespath = os.path.normpath(
        os.path.join(
            bpy.utils.script_path_user(),
            "addons",
            "modules"
        )
    )
    if not os.path.exists(modulespath):
        os.makedirs(modulespath)

    # set user modules path at beginning of paths for earlier hit
    if sys.path[1] != modulespath:
        sys.path.insert(1, modulespath)

    return modulespath

def install_dependencies():
    modulespath = modules_path()

    # Try to import PySpeckle and install if necessary using pip
    try:
        from subprocess import run as sprun
        try:
            import pip
        except:
            from subprocess import call
            print("Installing pip... "),
            #res = call("{} -m ensurepip".format(bpy.app.binary_path_python))
            res = sprun([bpy.app.binary_path_python, "-m", "ensurepip"])
            #res = call("{} -m pip install --upgrade pip==9.0.3".format(bpy.app.binary_path_python))

            if res == 0:
                import pip
            else:
                raise Exception("Failed to install pip.")

        print("Installing PySpeckle to \"{}\"... ".format(modulespath)),

        pip3 = "pip3"
        if sys.platform=="darwin":
            pip3 = os.path.normpath(
                os.path.join(
                os.path.dirname(bpy.app.binary_path_python),
                "..",
                "bin",
                pip3
                )
            )

        res = sprun([bpy.app.binary_path_python, "-m", "pip", "-V"])

        #res = pipmain(["install", "--upgrade", "--target", modulespath, "speckle"])        
        #res = pipmain(["install", "--upgrade", "speckle"])
        
        #res = sprun([pip3, "install", "-t", "\"{}\"".format(modulespath), "speckle"])
        res = sprun([bpy.app.binary_path_python, "-m", "pip", "install", "-q", "-t", "{}".format(modulespath), "--no-deps", "pydantic"])
        res = sprun([bpy.app.binary_path_python, "-m", "pip", "install", "-q", "-t", "{}".format(modulespath), "speckle"])
     
    except:
        raise Exception("Failed to run pip. Please make sure you have pip installed.")


try:
    import speckle
except ModuleNotFoundError as error:
    print("Speckle not found. Attempting to install dependencies...")
    install_dependencies()

from speckle import SpeckleApiClient, SpeckleCache

from bpy_speckle.ui.view3d import VIEW3D_PT_speckle, VIEW3D_UL_SpeckleAccounts, VIEW3D_UL_SpeckleStreams
from bpy_speckle.ui.object import OBJECT_PT_speckle
from bpy_speckle.properties.scene import SpeckleSceneSettings, SpeckleSceneObject, SpeckleUserAccountObject, SpeckleStreamObject
from bpy_speckle.properties.object import SpeckleObjectSettings
from bpy_speckle.properties.collection import SpeckleCollectionSettings
from bpy_speckle.operators.accounts import SpeckleLoadAccounts, SpeckleAddAccount, SpeckleImportStream2,SpeckleClearObjectCache, SpeckleClearAccountCache, SpeckleClearStreamCache, SpeckleLoadAccountStreams
from bpy_speckle.operators.object import SpeckleUpdateObject, SpeckleResetObject, SpeckleDeleteObject, SpeckleUploadObject, SpeckleUploadNgonsAsPolylines
from bpy_speckle.operators.streams import SpeckleViewStreamDataApi, SpeckleViewStreamObjectsApi, SpeckleDeleteStream, SpeckleSelectOrphanObjects
from bpy_speckle.operators.streams import SpeckleUpdateGlobal, SpeckleUploadStream, SpeckleCreateStream

from bpy_speckle.callbacks import scb_on_mesh_edit
from bpy.app.handlers import persistent


@persistent
def load_handler(dummy):
    bpy.ops.scene.speckle_accounts_load()


callbacks = [
    scb_on_mesh_edit,
    ]


classes = [
    VIEW3D_PT_speckle, 
    VIEW3D_UL_SpeckleAccounts, 
    VIEW3D_UL_SpeckleStreams,
    OBJECT_PT_speckle,
    SpeckleSceneObject, 
    SpeckleStreamObject,    
    SpeckleUserAccountObject,
    SpeckleSceneSettings, 
    SpeckleObjectSettings,
    SpeckleCollectionSettings,
]

classes.extend([
    SpeckleLoadAccounts, 
    SpeckleAddAccount, 
    SpeckleImportStream2,
    SpeckleClearObjectCache,
    SpeckleClearAccountCache, 
    SpeckleClearStreamCache,
    SpeckleLoadAccountStreams,
    ])

classes.extend([
    SpeckleUpdateObject,
    SpeckleResetObject, 
    SpeckleDeleteObject, 
    SpeckleUploadObject,
    SpeckleUploadNgonsAsPolylines,
    ])

classes.extend([
    SpeckleViewStreamDataApi, 
    SpeckleViewStreamObjectsApi, 
    SpeckleDeleteStream, 
    SpeckleSelectOrphanObjects, 
    SpeckleUpdateGlobal,
    SpeckleUploadStream,
    SpeckleCreateStream,
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
        #print("class: {} class_name: {}".format(cls, cls.__name__))

        if hasattr(bpy.types, cls.__name__):
            print("   already registered")
            unregister_class(cls)
        register_class(cls)

    bpy.types.Scene.speckle = bpy.props.PointerProperty(type=SpeckleSceneSettings)
    bpy.types.Collection.speckle = bpy.props.PointerProperty(type=SpeckleCollectionSettings)

    #from . properties.object import SpeckleObjectSettings
    bpy.types.Object.speckle = bpy.props.PointerProperty(type=SpeckleObjectSettings)

    bpy.types.Scene.speckle_client = SpeckleApiClient()
    bpy.types.Scene.speckle_cache = SpeckleCache()

    '''
    Add callbacks
    '''
    #if scb_on_mesh_edit not in bpy.app.handlers.depsgraph_update_pre:
    #    bpy.app.handlers.depsgraph_update_pre.append(scb_on_mesh_edit)

    handler = bpy.types.SpaceView3D.draw_handler_add(draw_speckle_info, (None, None), 'WINDOW', 'POST_PIXEL')
    bpy.app.handlers.load_post.append(load_handler)



def unregister():
    bpy.app.handlers.load_post.remove(load_handler)

    if handler:
        bpy.types.SpaceView3D.draw_handler_remove(handler, "WINDOW")

    '''
    Remove callbacks
    '''
    #if scb_on_mesh_edit in bpy.app.handlers.depsgraph_update_pre:
    #    bpy.app.handlers.depsgraph_update_pre.remove(scb_on_mesh_edit)        

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