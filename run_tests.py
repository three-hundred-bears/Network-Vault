
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

if __name__ == "__main__":
    enableHou()
    runner = unittest.TextTestRunner()
    tests = unittest.defaultTestLoader.discover("tests")

    runner.run(tests)
