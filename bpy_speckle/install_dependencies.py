import os
import ctypes, sys

def install_dependencies():
    import sys
    import os
    try:
        try:
            import pip
        except:
            from subprocess import run as sprun
            print("Installing pip... "),
            pyver = ""
            if sys.platform != "win32":
                pyver = "python{}.{}".format(
                    sys.version_info.major,
                    sys.version_info.minor
                )

            ensurepip = os.path.normpath(
                os.path.join(
                    os.path.dirname(sys.argv[1]),
                    "..", "lib", pyver, "ensurepip"
                )
            )
            res = sprun([sys.argv[1], ensurepip])

            if res.returncode == 0:
                import pip
            else:
                raise Exception("Failed to install pip.")

        modulespath = os.path.normpath(
            os.path.join(
                sys.argv[2],
                "addons",
                "modules"
            )
        )
        if not os.path.exists(modulespath):
           os.makedirs(modulespath) 
        print("Installing speckle to {}... ".format(modulespath)),

        try:
            from pip import main as pipmain
        except:
            from pip._internal import main as pipmain

        res = pipmain(["install", "--upgrade", "--target", modulespath, "speckle"])
        if res > 0:
            raise Exception("Failed to install speckle.")
    except:
        raise Exception("Failed to install dependencies. Please make sure you have pip installed.")
if __name__ == "__main__":

    try:
        import speckle
    except:
        print("Failed to load speckle.")
        from sys import platform
        if platform == "win32":
            if ctypes.windll.shell32.IsUserAnAdmin():
                install_dependencies()
                import speckle
            else:
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)

        else:
            print("Platform {} cannot automatically install dependencies.".format(platform))
            raise
