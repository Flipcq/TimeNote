import sys
from cx_Freeze import setup, Executable

build_exe_options = {"packages": ["os"], "includes": ["tkinter"]}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="TimeNote",
    version="0.1",
    description="A simple note-taking application that automatically calculates the reading time of the text you are writing.",
    options={"build_exe": build_exe_options},
    executables=[Executable("TimeNote.py", base=base)]
)