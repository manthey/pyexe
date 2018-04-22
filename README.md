# pyexe.exe

[![Build status](https://ci.appveyor.com/api/projects/status/n18f0997k18x87lw/branch/master?svg=true)](https://ci.appveyor.com/project/manthey/pyexe/branch/master)

I have often wanted a stand-alone version of python that is a single Windows executable.

It consists of the most recent versions of Python (with builds for 2.7, 3.5,
and 3.6 each in 32-bit and 64-bit versions), pywin32, psutil, six, pip, 
setuptools, and includes all packages that can be included without additional 
dlls, excepting tkinter.

See the appveyor script for build instructions.

## Installing other modules

Python is most useful with additional modules.  The stand-alone executable can use pip to install modules from pypi to the local directory.  For instance:

```python
py36-64.exe -m pip install --no-cache-dir --target . --upgrade sympy
```

Use `-m pip` to run the pip module.  Use `--no-cache-dir` to avoid writing files to the user's data directory.  Use `--target .` to install to the current directory, allowing you to import the modules easily.  Use `--upgrade` to replace existing files, such as the common `bin` directory.  Note that using `--upgrade` will overwrite or discard existing files, which may not be what you want (the `bin` directory will end up with just files for the most recently installed package).
