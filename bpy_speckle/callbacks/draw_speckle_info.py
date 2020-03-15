# Drawing callback to display active Speckle account
import blf
import bpy

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