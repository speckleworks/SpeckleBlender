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
    "wiki_url": "https://github.com/speckleworks/SpeckleBlender",
    "category": "Scene",
}

import bpy

'''
Import PySpeckle and attempt install if not found
'''

try:
    import speckle
except ModuleNotFoundError as error:
    print("Speckle not found. Attempting to install dependencies...")
    from .install_dependencies import install_dependencies
    install_dependencies()

'''
Import SpeckleBlender classes
'''

from speckle import SpeckleApiClient, SpeckleCache

from bpy_speckle.ui import *
from bpy_speckle.properties import *
from bpy_speckle.operators import *
from bpy_speckle.callbacks import *
from bpy.app.handlers import persistent


# Add load handler to initialize Speckle when 
# loading a Blender file
@persistent
def load_handler(dummy):
    bpy.ops.scene.speckle_accounts_load()


# Permanent handle on callbacks
callbacks = {}

speckle_classes = []
speckle_classes.extend(operator_classes)
speckle_classes.extend(property_classes)
speckle_classes.extend(ui_classes)

def register():
    from bpy.utils import register_class
    for cls in speckle_classes:
        register_class(cls)

    # Register all properties

    bpy.types.Scene.speckle = bpy.props.PointerProperty(type=SpeckleSceneSettings)
    bpy.types.Collection.speckle = bpy.props.PointerProperty(type=SpeckleCollectionSettings)

    bpy.types.Object.speckle = bpy.props.PointerProperty(type=SpeckleObjectSettings)

    bpy.types.Scene.speckle_client = SpeckleApiClient()
    bpy.types.Scene.speckle_cache = SpeckleCache()

    '''
    Add callbacks
    '''

    #if scb_on_mesh_edit not in bpy.app.handlers.depsgraph_update_pre:
    #    bpy.app.handlers.depsgraph_update_pre.append(scb_on_mesh_edit)

    callbacks['view3d_status'] = ((
        bpy.types.SpaceView3D.draw_handler_remove, # Function pointer for removal
        bpy.types.SpaceView3D.draw_handler_add(draw_speckle_info, (None, None), 'WINDOW', 'POST_PIXEL'), # Add handler
        'WINDOW' # Callback space for removal
        ))

    bpy.app.handlers.load_post.append(load_handler)

def unregister():

    bpy.app.handlers.load_post.remove(load_handler)

    '''
    Remove callbacks
    '''

    for cb in callbacks.values():
        cb[0](cb[1], cb[2])

    #if scb_on_mesh_edit in bpy.app.handlers.depsgraph_update_pre:
    #    bpy.app.handlers.depsgraph_update_pre.remove(scb_on_mesh_edit)        

    from bpy.utils import unregister_class
    for cls in reversed(speckle_classes):
        unregister_class(cls)

if __name__ == "__main__":
    register()
