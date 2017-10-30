import sys
from cx_Freeze import setup, Executable

base = 'Win32GUI'
version = "2.0.2"

exe = Executable(
    script="programm.py",
    icon="resource/logo_tfortis.ico",
    targetName="tfortis.exe",
    compress=True,
    base=base
)
includefiles = [("resource/tfortis_ico.ico", "resource/tfortis_ico.ico"),
                ("resource/main_window.ui", "resource/main_window.ui"),
                ("resource/edit_window.ui", "resource/edit_window.ui"),
                ("resource/logo_tfortis.ico", "resource/logo_tfortis.ico"),
                ("resource/ajax-loader.gif", "resource/ajax-loader.gif"),
                "CHANGELOG.txt",
                ]

excludes = ['_gtkagg', '_tkagg', 'bsddb', 'curses', 'email', 'pywin.debugger',
            'pywin.debugger.dbgcon', 'pywin.dialogs', 'tcl', 'Tkconstants', 'Tkinter']

setup(

    version=version,
    url='www.tfortis.ru',
    maintainer="Suvorov D.",
    name="TFortis Scanner",
    description="TFortis Scanner. Fort-Telecom Ltd.",
    author="Fort-Telecom Ltd.",
    options={'build_exe': {"include_files": includefiles,
                           "include_msvcr": True,
                           "excludes": excludes,
                           "optimize": 2
                           }
             },
    executables=[exe]
)
