#!/usr/bin/python
#
# Copyright 2013, 2014 David Manthey
#
# This is the setup file to create a stand-along python interpreter for
# Windows.  Run "python setup.py py2exe" to build.  This results in an
# executable called py.exe, which can then run an arbitrary python script on
# Windows via py.exe (name of script).

import os
import sys
#from setuptools import setup
from distutils.core import setup
# must be after setup
import py2exe
import py2exe.resources.VersionInfo
# Our include
from py_version import Version, Description

# I wanted to include msvcr90.dll to make this more truely stand-alone, but it
# won't include.
#origIsSystemDLL = py2exe.build_exe.isSystemDLL
#def isSystemDLL(pathname):
#   if os.path.basename(pathname).lower() in ("msvcp71.dll", "dwmapi.dll", "msvcr90.dll"):
#      return 0
#   return origIsSystemDLL(pathname)
#py2exe.build_exe.isSystemDLL = isSystemDLL

setup(
   console = [{
      "script":"py.py",
      "other_resources":[(py2exe.resources.VersionInfo.RT_VERSION, 1, py2exe.resources.VersionInfo.Version(
            version = Version,
            company_name = "David Manthey",
            file_description = Description,
            legal_copyright = "Copyright 2013, 2014 David Manthey",
            product_name =  Description,
            product_version = Version
            ).resource_bytes())],
      }],
   options = {
      "py2exe": {
         "dist_dir":"dist",
         "bundle_files": 1, # bundle as much as possible
         "compressed": True,
         # If we turn on optimizations, then some things, such as sympy, which
         # depend on docstring manipulation will fail
         # "optimize": 2,
      }},
   # include all python files in the executable, not in library.zip
   zipfile = None,
   )

