# SpeckleBlender
Speckle add-on for Blender 2.8

## Updates

### July 10, 2019

Important update: `SpeckleBlender` now checks for the `speckle` dependency and installs it if necessary, using `pip`. If `pip` is not found, it tries installing that too. This should make installing / setup easier. 

Database updating / loading should work better now too. Logging in works, and a user database is created if none exists, with some uniqueness constraints. This prevents duplicate user accounts from appearing in the account list.

### July 10, 2019

Added the `2-80` branch for supporting Blender 2.8. This will eventually replace the master branch, so work on the 2.79 version will probably not continue.

The Speckle UI can be found in the 3d viewport toolbar (N), under the Speckle tab.

Also - importantly - PySpeckle has been undergoing changes and improvements, so these will slowly filter into SpeckleBlender. Take care when installing `speckle` through `pip` - hopefully there won't be any breaking changes anytime soon, but keep that in mind.

### January 13, 2019

This update adds support for loading local user accounts and logging in with a new account. New logged in accounts will be saved to disk. Loading an account also lists all the available streams for that account.

### November 15, 2018

This update separates the plug-in into a generic Python client which is available through `pip` and a Blender add-on interface. 

## Disclaimer
This code is very WIP and as such should be used with extreme caution, on non-sensitive projects.
There is much to be tightened up, optimized, organized, etc. but the basic functionality is there.

## Installation

Install [PySpeckle](https://github.com/speckleworks/PySpeckle) through `pip`, making sure to use Blender's Python. Installing `pip` for Blender is possible, and is done as usual except taking care to make sure that you are operating in Blender's Python environment.

`pip install speckle`


The add-on works like a normal Blender add-on:
1. Download the 'bpy_speckle' folder
2. Place into 'BLENDER_DIRECTORY/VERSION#/scripts/addons_contrib'
3. Start Blender
4. Go to User Preferences (Ctrl + Alt + U)
5. Go to the Add-ons tab
6. Find and enable `Speckle Blender` in the Testing category
7. Click Save User Settings

## Usage

Usage is fairly simple, but for now is with a couple caveats:
1. Currently, only Mesh objects are supported. Importing Breps is possible, but will only import their display mesh. Polylines and curves will be introduced soon. Anything else will be ignored. 
2. Streams have to be reloaded to see their changes. Automatic refreshing and updates will hopefully be eventually implemented.

**SpeckleBlender** can be used as follows:
- In the Speckle.Works panel, press `Add Account` to login with an existing profile. This will save the authentication in the local Speckle user database.
- Alternatively, press `Load Accounts` to load all local users, either from the database or from the older local profile folder.
- The `Streams` list should be automatically populated with the available streams for the selected user. 
- Select a stream and press `Load Stream`. This will load all objects in that stream into a new Collection, identified by the stream ID. 
- Pressing `View stream data (API)` or `View stream objects (API)` will open the stream in your web browser.

At the moment, that is about the extent of SpeckleBlender capabilities for Blender 2.8. Adding objects to streams, creating new streams, etc. will slowly be added back in. 

Two useful things:
- **SpeckleBlender** will look for a `texture_coordinates` property and use that to create a UV layer for the imported object. These texture coordinates are a space-separated list of floats (`[u v u v u v etc...]`) that is encoded as a base64 blob. 
- If a `material` property is found, **SpeckleBlender** will create a material named using the sub-property `material.name`. If a material with that name already exists in Blender, **SpeckleBlender** will just assign that existing material to the object. This allows geometry to be updated without having to re-assign and re-create materials.

## Notes
SpeckleBlender is written and maintained by [Tom Svilans](http://tomsvilans.com) ([Github](https://github.com/tsvilans)).
