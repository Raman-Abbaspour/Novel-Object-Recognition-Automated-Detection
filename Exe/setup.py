# from distutils.core import  setup
# import py2exe
#
# setup(console=["Test.py"],
#       options={
#           "py2exe": {
#               "optimize": 2,
#               # "includes": ["mf1.py", "mf2.py", "mf3.py"],  # List of all the modules you want to import
#               "includes": ["tensorflow"]  # List of the package you want to make sure that will be imported
#           }
#       }
#       )

# help (setup)
from cx_Freeze import setup, Executable
import platform
import os

if platform.system() == "Windows":
      PYTHON_DIR = os.path.dirname(os.path.dirname(os.__file__))
      os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_DIR,
                                               'tcl', 'tcl8.6')
      os.environ['TK_LIBRARY'] = os.path.join(PYTHON_DIR,
                                              'tcl', 'tk8.6')



include_files = [
(os.path.join(PYTHON_DIR, 'DLLs', 'tcl86t.dll'), ''),
(os.path.join(PYTHON_DIR, 'DLLs', 'tk86t.dll'), ''),
("saved_model","saved_model")
]






setup(name = "NORAD" ,
      version = "0.1" ,
      description = "Beta" ,
      executables = [Executable("Main.py", base = "Win32GUI")],
      options ={
      'build_exe': {
      'packages': ['tensorflow'],
      'excludes': ['scipy',"numba","sklearn"],
      'include_files':include_files


      }}
)




