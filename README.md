# pyexe.exe

[![Build status](https://github.com/manthey/pyexe/actions/workflows/build.yml/badge.svg)](https://github.com/manthey/pyexe/actions/workflows/build.yml)

Here is a stand-alone version of python that is a single Windows executable.

It consists of recent versions of Python (with 64-bit builds for 3.11 through
3.15, plus free-threaded builds for 3.14t and 3.15t), pywin32, psutil (not in
the free-threaded builds), pip, setuptools, and includes all packages that can
be included without additional dlls, excepting tkinter.

See the GitHub Actions workflow (.github/workflows/build.yml) for build
instructions.

## Development and testing

The test suite runs pyexe.py from a source checkout against a python
interpreter, plus the pyexe-marked tests that only apply to a built
stand-alone executable (the CI workflow builds the executables and runs the
full suite against them).

The simplest way to run the tests is with tox, which creates an isolated
environment and follows the same recipe as the CI workflow (generate
`py_version.py` from the git tags with setuptools_scm, build the sample
zipapp, run pytest):

```bash
python -m pip install --upgrade tox
tox
```

To run the tests manually, install the development dependency group from
`pyproject.toml`, then run pytest from the `tests` directory (the sample
files are referenced relative to it).  The tests that install packages with
pip into the current directory remove what they installed, so no cleanup is
needed between runs:

```bash
python -m pip install --upgrade --group dev
cd tests
python -m zipapp --output ../sample_zipapp.pyz -p "/usr/bin/env python" sample_zipapp
python -m pytest -l --cache-clear --exe="/path/to/python" -m "not pyexe"
```

If a test run is interrupted, the residue of the interrupted run may remain
in the `tests` directory, and subsequent collection may fail until it is
removed (the CI workflow removes it with `git clean -fxd .`, which is safe
there since the checkout is disposable).

Use a python from a full installation (or a built stand-alone executable)
for `--exe`; a virtual environment's python does not import from the
executable directory, and the tests skip the checks that do not apply to
it.  To install a full python.org build for testing or for building the
executables, use `install_python.py` (it requires the Windows Installer
service, so it does not work in restricted environments such as some
sandboxes).

To run the linters and formatters that the pre-commit configuration enforces,
install the development dependency group and run
`pre-commit run --all-files`.

## Installing other modules

Python is most useful with additional modules.  The stand-alone executable can use pip to install modules from pypi to the local directory.  For instance:

```bash
py314.exe -m pip install --no-cache-dir --target . --upgrade sympy
```

Use `-m pip` to run the pip module.  Use `--no-cache-dir` to avoid writing files to the user's data directory.  Use `--target .` to install to the current directory, allowing you to import the modules easily.  Use `--upgrade` to replace existing files, such as the common `bin` directory.  Note that using `--upgrade` will overwrite or discard existing files, which may not be what you want (the `bin` directory will end up with just files for the most recently installed package).

## Differences from installed Python

Although the stand-alone Python attempts to have the same features as a normally installed Python, there are some differences.

- If command line options are specified, there may be some differences in `sys.flags`, since it is read-only and cannot be altered after start.
- `PYTHONHOME` is ignored.  This option doesn't make sense for a stand-alone version.
- `-V` and `PYTHONVERBOSE` don't print exactly the same information as installed Python, partly because the verbosity is increased after some modules are already imported.
- `--check-hash-based-pycs` is ignored.  This option cannot be changed after the Python executable starts.
- `-R` and `PYTHONHASHSEED` are ignored.  These options cannot be changed after the Python executable starts.
- `-X` options are accepted but not applied, since implementation-specific options cannot be changed after the Python executable starts.
- `-v` and `PYTHONVERBOSE` are accepted but cannot be applied in Python 3.11+, since the interpreter no longer consults the legacy `Py_VerboseFlag` global after startup.
- `-b`, `-bb`, and `PYTHONDONTWRITEBYTECODE`-style bytes warnings (`-b`, `PYTHONWARNINGS` still work) are accepted, but the `BytesWarning` flag cannot be applied in Python 3.11+, since the legacy `Py_BytesWarningFlag` global is no longer consulted after startup.
- `-O` and `-OO` are emulated: modules imported after start are compiled with the requested optimization level, and bytecode cache files use the matching `opt-N` tag.  Modules already imported at startup are unaffected.
- `PYTHONCASEOK` is honored, and ignored when `-E` or `-I` is given, matching
  Python 3.9+.  It is applied by patching the import system, since PyInstaller
  starts the interpreter in isolated mode.
- `PYTHONIOENCODING` is honored, in the form `encoding:errors`, and ignored
  when `-E` or `-I` is given.  It changes the encoding and error handler of
  `sys.stdin`, `sys.stdout`, and `sys.stderr` after the interpreter has
  started, which is equivalent to how the python executable applies it at
  startup.
- `-I` and `-E` are applied to pyexe's own environment handling, but the interpreter itself has already been started in a mode that ignores most environment variables.
- Not all environment variables are handled, such as: `PYTHONFAULTHANDLER`, `PYTHONLEGACYWINDOWSFSENCODING`, `PYTHONLEGACYWINDOWSSTDIO`, `PYTHONMALLOC`, `PYTHONDEVMODE`.  Some of these are ignored; some are used and cannot be suppressed with `-E` or `-I`.  Many of these could be handled properly with additional work.
- `PYTHONSAFEPATH` is honored, and `-P` suppresses the automatic prepending of the script directory or current directory to `sys.path`.
