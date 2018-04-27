# Release Notes

## Unreleased

### Changes

- Added support for zipapps.
- Added support for `PYTHONPATH`.

## Version 12

### Changes

- Removed some modules that can't be imported without Scintilla.DLL.
- Ignore standard Python command line options that aren't implemented.
- The banner in interactive mode better matches native Python.

### Bug Fixes

- Fixed raw input on Python 3.
- Fixed handling - on the command line.
- Fixed combining -i with -c or -m.
- Unbuffered interactive mode fixed on Python 3.

### Build

- Added tests to show that pyexe's behavior is the same as native Python.
- Added tests for help, reading from stdin, reading in tty mode, hyphen mode, and the `--all` flag.

## Version 11

### Changes

- Explicitly include `six`, `pip`, and `setuptools`
- Update to the Python 2.7.14, 3.5.3, 3.6.4.
- Update to pywin32 223, pip 10.0.1, psutil 5.4.5, setuptools 39.0.1, six 1.11.0
- Improved version reporting (PR #9)
- More of pywin32 is included thanks to PyInstaller

### Build

- Moved to GitHub
- Built for Python 2.7, 3.5, 3.6 in 32-bit and 64-bit variants
- Built on appveyor using PyInstaller
- Add CI tests for installing and importing pip libraries, testing multiprocessing.

## Version 10

- Upgraded to Python 2.7.9
- Added psutil 2.1.3 
- Added support for the `-m` option.
- Turned off the optimization flag when building.  Having it on interferes with some modules (such as sympy) which rely on docstring manipulation.

## Version 9:
- Revert changes to global dictionaries to fix multiprocessing forking.

## Version 8

- Fixed a bug introduced in version 7 when renaming the variable `loc`.

## Version 7:

- Added support for `-E`, `-x`, and `--version` options.
- Changed how the globals / locals dictionaries are used for greater consistency in different execution modes.
- Accept multiple single letter command line options grouped together.

## Version 6

- Added support for multiprocessing forking
- Added support for non-tty direct usage (input and output pipes, for instance)
- Added support for `-i` option and `PYTHONINSPECT` environment variable.
- Turned off "frozen" flag in the executable.
- Upgraded pywin32 to build 219 (was 218).
- Upgraded to Python 2.7.8
- Added `import site` to interactive prompts to get help and other commands added to the builtins.
- Added support for unbuffered `-u` option and `PYTHONUNBUFFERED` environment variable.

## Version 5

- Imported submodules, such as logging.handlers, since they weren't included implicitly.

## Version 4

- Upgraded to Python 2.7.5

## Version 3

- Added the program path to `sys.path` when running a program, and `''` to `sys.path` when running direct or interpreted.

## Version 2

- fixed an issue with __file__ and __name__

## Version 1

- initial release


