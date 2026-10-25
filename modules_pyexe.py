#!/usr/bin/python

import importlib
import os
import pkgutil
import re
import sys

# Modules we know we can't work with or are completely pointless
ExcludeModules = [
    # our own code
    'pyexe', 'modules_pyexe', 'modules_pyexe_list', 'install_python',
    # installers and modules the installers require
    'py2exe',
    'PyInstaller', '_pyinstaller_hooks_contrib', 'pyinstaller_hooks_contrib',
    'pefile', 'macholib', 'altgraph', 'distlib', 'virtualenv',
    'ordlookup', 'peutils',
    # test
    'test', 'tests',
    # Pointless modules
    'antigravity', 'this', 'lib2to3.__main__', 'unittest.__main__',
    # Modules that aren't installed, so that they are excluded if they are
    # ever installed (tkinter is not installed, since it needs tcl/tk dlls)
    '_tkinter',
    'tkinter', 'turtle',
    'turtledemo', 'tcl', 'tk',
    # These would fail to be imported by the tests
    'idlelib', 'win32traceutil',
    # These cause the import machinery to block forever in the stand-alone
    # executable, in ways that depend on the modules that were imported
    # before them (measured with the pywin32 312 modules): the editor module
    # adds a document template to the Pythonwin application at import, and
    # the other modules import it or similar GUI machinery.  adodbapi also
    # blocks in some contexts.
    'adodbapi',
    'pywin.debugger', 'pywin.dialogs.ideoptions',
    'pywin.framework.dbgcommands', 'pywin.framework.editor',
    'pywin.framework.interact', 'pywin.framework.intpyapp',
    'pywin.framework.startup', 'pywin.framework.stdin',
    'pywin.framework.winout', 'pywin.scintilla', 'pywin.tools.TraceCollector',
    # Importing start_pythonwin launches the Pythonwin GUI application, which
    # blocks forever while waiting for the message loop.
    'start_pythonwin',
    # The axdebug modules cannot work, since the axdebug dll is not available.
    'win32com.axdebug.debugger', 'win32com.axdebug.dump',
    'win32com.axscript.client.debug',
]
# Exclude examples, tests, vendor directories, and Tk.  Some of these won't
# exist in the default installation
ExcludeParts = [
    'examples', 'demos', 'test', 'tests', 'testsuite', 'testing',
    'test_manage', 'Tk', '_vendor', 'vendor']


def walk_packages(path=None, prefix=''):
    """
    Walk modules and packages recursively, similar to pkgutil.walk_packages,
    but do not descend into excluded package components (vendor directories,
    tests, examples, etc.), since the modules there should not be exposed as
    importable top level or submodule names.
    """
    for finder, name, ispkg in pkgutil.iter_modules(path, prefix):
        yield finder, name, ispkg
        if ispkg and not any(
                part in ExcludeParts for part in name.split('.')):
            try:
                module = importlib.import_module(name)
                subpath = list(getattr(module, '__path__', []))
            except Exception:
                subpath = []
            yield from walk_packages(subpath, name + '.')


def excluded_by_path(module):
    """
    Check if a module is located in a directory that should not be exposed,
    such as a vendor directory, examples, or tests.

    Enter: module: the imported module to check.
    Exit:  True if the module is in an excluded directory.
    """
    filepath = getattr(module, '__file__', None) or ''
    parts = os.path.normpath(os.path.dirname(os.path.abspath(filepath))).split(os.sep)
    return any(part in ExcludeParts for part in parts)


def install_distutils_alias_finder():
    """
    Install a sys.meta_path finder that supplies setuptools._distutils as
    the distutils package.
    """
    # In the stand-alone executable, PyInstaller aliases the distutils
    # package to setuptools._distutils, and the setuptools modules are
    # written to work with the setuptools distutils.  Make the module list
    # generation use the same distutils, so that the same modules are
    # collected and bundled.  Otherwise, on python 3.11, the
    # setuptools._distutils submodules cannot be imported (the python 3.11
    # standard library distutils lacks some of the modules that they
    # require, such as distutils._log), so those modules are dropped from
    # the module list, and the setuptools.command modules that import them
    # through the distutils alias fail to import in the stand-alone
    # executable, where distutils is the setuptools distutils.
    #
    # The _distutils_hack finder that setuptools installs redirects
    # distutils the same way, but importing pip, which is one of the
    # collected modules, makes the hack clear the aliased distutils modules
    # and permanently disable its redirect, so that the standard library
    # distutils is used from then on (the hack ensures the standard library
    # distutils when running under pip on python 3.11 and earlier).
    # Instead, use a finder of our own, which always supplies
    # setuptools._distutils as distutils.
    try:
        import setuptools._distutils  # noqa: F401
    except ImportError:
        return
    import importlib.abc
    import importlib.util

    class DistutilsAliasFinder:
        """Supply setuptools._distutils as the distutils package."""

        def find_spec(self, fullname, path=None, target=None):
            if fullname != 'distutils':
                return None
            module = importlib.import_module('setuptools._distutils')

            class loader(importlib.abc.Loader):
                def create_module(self, spec):
                    module.__name__ = 'distutils'
                    return module

                def exec_module(self, module):
                    pass

            return importlib.util.spec_from_loader(
                fullname, loader(), origin=module.__file__)

    sys.meta_path.insert(0, DistutilsAliasFinder())


def list_modules():
    """
    Get a list of all modules and submodules in the system that we can import.

    Exit:  modules: a list of modules.
           report: a list of lines reporting what was included and excluded,
                   and why.
    """
    # Snapshot sys.path before importing anything; some packages (such as
    # setuptools) add their own vendored directories to sys.path on import,
    # and modules in those directories should not be included.
    basepath = list(sys.path)
    install_distutils_alias_finder()
    modules = set()
    for item in walk_packages(basepath):
        modules.add(item[1])
    collected = sorted(modules)
    # Remove modules with dashes in their names
    modules = [item for item in collected if '-' not in item]
    # Remove modules starting with values in ExcludeModules or containing a
    # module component in ExcludeParts
    regex = re.compile(
        r'(^(' + '|'.join([re.escape(val) for val in ExcludeModules]) +
        r')|\.(' + '|'.join([re.escape(val) for val in ExcludeParts]) +
        r'))(\.|$)')
    staticexcluded = [item for item in modules if regex.search(item)]
    modules = [item for item in modules if not regex.search(item)]
    modules.sort()

    # win32ui initializes the MFC state that some modules, such as dde,
    # require to be present before they can be imported.  Import it before
    # the other modules so those modules work with the --all flag.
    if 'win32ui' in modules:
        modules.remove('win32ui')
        modules.insert(0, 'win32ui')
    failures = []
    for item in modules[:]:
        try:
            # If we already imported the module based on a previous import, we
            # don't need to include it explicitly
            if item in sys.modules and '.' in item:
                modules.remove(item)
                continue
            sys.stderr.write('? %s\r' % item)
            sys.stderr.flush()
            mod = importlib.import_module(item)
            if excluded_by_path(mod):
                raise ImportError('Excluded path: %s' % getattr(mod, '__file__', ''))
            sys.stderr.write('+ %s\n' % item)
            sys.stderr.flush()
        except BaseException as exception:
            # If the import fails, remove the modules from the list
            modules.remove(item)
            failures.append('%s: %s: %s' % (
                item, type(exception).__name__, exception))
            sys.stderr.write('- %s\n' % item)
            sys.stderr.flush()
    report = ['Bundled modules: %d' % len(modules),
              'Excluded because they failed to import: %d' % len(failures)]
    report.extend('    %s' % failure for failure in failures)
    report.append('Excluded by the static exclusion lists: %d' %
                  len(staticexcluded))
    for val in ExcludeModules:
        matched = [name for name in collected
                   if name == val or name.startswith(val + '.')]
        if matched:
            report.append('    %s: %d' % (val, len(matched)))
    for part in ExcludeParts:
        matched = [name for name in collected if part in name.split('.')]
        if matched:
            report.append('    %s: %d' % (part, len(matched)))
    stale = [val for val in ExcludeModules
             if not any(name == val or name.startswith(val + '.')
                        for name in collected)]
    report.append('Stale static exclusions: %s' %
                  (', '.join(stale) if stale else 'none'))
    report.append('Bundled module names:')
    report.extend('    %s' % name for name in modules)
    return modules, report


if __name__ == '__main__':
    pyexePath = None
    Help = False
    for arg in sys.argv[1:]:
        if arg.startswith('-'):
            if arg.startswith('--exclude='):
                ExcludeModules.extend(arg.split('=', 1)[1].split(','))
            elif arg.startswith('--exclude-part='):
                ExcludeParts.extend(arg.split('=', 1)[1].split(','))
            else:
                Help = True
        elif not pyexePath:
            pyexePath = arg
        else:
            Help = True
    if Help:
        print("""Generate a list of importable system modules.

Syntax: modules_pyexe.py [pyexe.py]
             [--exclude=(comma-separated list of module names)]
             [--exclude-part=(comma-separated list of module component names)]

If a path is specified, the pyexe.py file is altered.  If no path is specified,
the module list is written to stdout.""")
        sys.exit(0)
    modules, report = list_modules()
    listPath = os.path.join(
        os.path.dirname(os.path.abspath(pyexePath)) if pyexePath else '.',
        'modules_pyexe_list.py')
    with open(listPath, 'w') as fptr:
        fptr.write('# Generated by modules_pyexe.py.  Do not edit.\n')
        for item in modules:
            fptr.write('import %s\n' % item)
    reportPath = os.path.join(
        os.path.dirname(os.path.abspath(pyexePath)) if pyexePath else '.',
        'modules_pyexe_report.txt')
    with open(reportPath, 'w') as fptr:
        fptr.write('\n'.join(report) + '\n')
    print('Wrote %s' % listPath)
    print('Wrote %s' % reportPath)
    # Print the report summary, without the list of bundled module names,
    # which is only in the report file.
    print('\n'.join(report[:report.index('Bundled module names:')]))
    if pyexePath:
        head = b'    # IMPORT ALL MODULES'
        tail = b'    # END IMPORT ALL MODULES'
        data = open(pyexePath, 'rb').read()
        # Guard each import individually, so that a module that cannot be
        # imported in the stand-alone executable is reported to stderr
        # without preventing the remaining bundled modules from being
        # imported.  Also write the name of each module to stderr before it
        # is imported, so that a module that hangs on import can be
        # identified by the last name written.
        imports = ('\n' + ''.join([
            '        sys.stderr.write("? ' + item + '\\r")\n'
            '        sys.stderr.flush()\n'
            '        try:\n'
            '            import ' + item + '\n'
            '        except BaseException as _exception:\n'
            '            sys.stderr.write("Failed to import ' + item + ': %r\\n" % _exception)\n'
            '            sys.stderr.flush()\n'
            for item in modules])).encode('utf8')
        data = data.split(head, 1)[0] + head + imports + tail + data.split(tail, 1)[1]
        open(pyexePath, 'wb').write(data)
    else:
        for item in modules:
            print('import %s' % item)
