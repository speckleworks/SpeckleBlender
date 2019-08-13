# SpeckleBlender
Speckle add-on for Blender 2.8


Important update: `SpeckleBlender` now checks for the `speckle` dependency and installs it if necessary, using `pip`. If `pip` is not found, it tries installing that too. This should make installing / setup easier. 

The Speckle UI can be found in the 3d viewport toolbar (N), under the Speckle tab.


## Disclaimer
This code is WIP and as such should be used with extreme caution, on non-sensitive projects.

## Installation

1. Place `bpy_speckle` folder in your `addons` folder. On Windows this is typically `%APPDATA%/Blender Foundation/Blender/2.80/scripts/addons`.
2. If `pip` is not installed in your Blender Python build, run Blender with admin privileges. Otherwise, start Blender as normal.
3. **SpeckleBlender** installs and upgrades **PySpeckle** and its dependencies automatically. It will install these in the `%APPDATA%/Blender Foundation/Blender/2.80/scripts/addons/modules` folder.
4. Go to `Edit->Preferences` (Ctrl + Alt + U)
5. Go to the `Add-ons` tab
6. Find and enable `SpeckleBlender` in the `Scene` category
7. In the 3d viewport, press `N` to bring up the 3d viewport toolbar.
8. The Speckle UI can be found in the 3d viewport toolbar (N), under the `Speckle` tab.

## Usage

- Click on `Load Accounts` to load all available local Speckle user profiles. This will populate the `Streams` list with available streams for the selected user.
- Click on `Add Account` to login and add a user profile to the local Speckle database.
- Click on `Load Stream` to load the selected stream. You can filter the stream by entering a query into the `Filter` field (i.e. `properties.weight>10` or `type="Mesh"`). The stream objects will be loaded into a Blender Collection, named `SpeckleStream_<STREAM_NAME>_<STREAM_ID>`.
- Click on `Delete Stream` to delete a stream. This will ask you to confirm the deletion, and also offer the option of deleting the accompanying Blender Collection if it exists.
- Click on `View stream data (API)` and `View stream objects (API)` to view the stream and stream objects in your web browser.

The `Cache` section provides some operators to manipulate the local Speckle database. For now it is just possible to clear the object and stream caches, and clear all user profiles from the database. Use with care.

## Caveats

- For now, only loading streams into Blender is possible. Uploading streams and synchronizing Speckle streams with Blender Collections will be implemented in the future.
- Mesh objects are supported. Breps are imported as meshes using their `displayValue` data. Curves have limited support: `Polylines` are supported; `NurbsCurves` are supported, though they are not guaranteed to look the same; `Lines` are supported; `Arcs` are not supported, `PolyCurves` are supported for linear / polyline segments but not arc segments.

## Custom properties

- **SpeckleBlender** will look for a `texture_coordinates` property and use that to create a UV layer for the imported object. These texture coordinates are a space-separated list of floats (`[u v u v u v etc...]`) that is encoded as a base64 blob. 
- If a `material` property is found, **SpeckleBlender** will create a material named using the sub-property `material.name`. If a material with that name already exists in Blender, **SpeckleBlender** will just assign that existing material to the object. This allows geometry to be updated without having to re-assign and re-create materials.
- Vertex colors are supported. The `colors` list from Speckle meshes is translated to a vertex color layer.
- Speckle properties will be imported as custom properties on Blender objects. Nested dictionaries are expanded to individual properties by flattening their key hierarchy. I.e. `propA:{'propB': {'propC':10, 'propD':'foobar'}}` is flattened to `propA.propB.propC = 10` and `propA.propB.propD = "foobar"`.

## Notes
SpeckleBlender is written and maintained by [Tom Svilans](http://tomsvilans.com) ([Github](https://github.com/tsvilans)).
