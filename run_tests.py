
import os, sys, unittest
import PySide2

def enableHou():

    if hasattr(sys, "setdlopenflags"):
        old_dlopen_flags = sys.getdlopenflags()
        sys.setdlopenflags(old_dlopen_flags | os.RTLD_GLOBAL)

    if sys.platform == "win32" and hasattr(os, "add_dll_directory"):
        os.add_dll_directory("{}/bin".format(os.environ["HFS"]))

    try:
        import hou
    except ImportError:
        sys.path.append(os.environ["HHP"])
        import hou
    finally:
        if hasattr(sys, "setddlopenflags"):
            sys.setdlopenflags(old_dlopen_flags)

def enableNetworkSaver():
    sys.path.append(os.path.abspath("python"))

if __name__ == "__main__":
    enableNetworkSaver()
    enableHou()
    runner = unittest.TextTestRunner()
    tests = unittest.defaultTestLoader.discover("tests")

    runner.run(tests)
