import sys
import os.path
from cx_Freeze import setup, Executable

PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))

base = None

if sys.platform == 'win32':
    base = 'Win32GUI'

executables = [
    Executable(
        'iv.py',
        base=base, 
        icon="icon.ico"
    )
]


options = {
    'build_exe': {
        "packages":[],
        'include_files':[
            "icon.ico",
            "iv.png",
         ],
    },
}

setup(
    name="Image Viewer",
    version="2018",
    description="QT5 Image Viewer Widget",
    options=options,
    executables=executables
)
