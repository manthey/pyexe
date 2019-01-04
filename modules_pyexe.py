#!/usr/bin/python

import importlib
import os
import re
import six
import subprocess
import sys

# Modules we know we can't work with or are completely pointless
ExcludeModules = [
    # our own code
    'pyexe', 'modules_pyexe', 'modules_pyexe_list',
    # installers and modules the installers require
    'py2exe',
    'PyInstaller', 'pefile', 'macholib', 'dis3', 'future', 'altgraph',
    'ordlookup', 'peutils', 'libfuturize', 'libpasteurize', 'past',
    # test
    'test', 'tests', 'asyncio.test_utils',
    # Pointless modules
    'antigravity', 'this', 'lib2to3.__main__', 'unittest.__main__',
    # Modules in appveyor that shouldn't be included, plus tkinter
    'Canvas', 'Dialog', 'FileDialog', 'FixTk', 'ScrolledText', 'SimpleDialog',
    'Tix', 'Tkconstants', 'Tkdnd', 'Tkinter', '_markupbase', '_tkinter',
    'adodbapi', 'altgraph', 'tkColorChooser', 'tkCommonDialog', 'tkFileDialog',
    'tkFont', 'tkMessageBox', 'tkSimpleDialog', 'tkinter', 'ttk', 'turtle',
    'turtledemo', 'tcl', 'tk', 'Tkinter',
    # These cause test importation fail
    'idlelib', 'win32traceutil', 'venv',
    # These cause --all flag to fail
    'pywin.debugger', 'pywin.dialogs.ideoptions',
    'pywin.framework.dbgcommands', 'pywin.framework.editor',
    'pywin.framework.interact', 'pywin.framework.intpyapp',
    'pywin.framework.startup', 'pywin.framework.stdin',
    'pywin.framework.winout', 'pywin.scintilla', 'pywin.tools.TraceCollector',
    'win32com.axdebug.debugger', 'win32com.axdebug.dump',
    'win32com.axscript.client.debug',
]
# Exclude examples, tests, and Tk.  Some of these won't exist in the default
# installation
ExcludeParts = [
    'examples', 'demos', 'test', 'tests', 'testsuite', 'testing',
    'test_manage', 'Tk']


def list_modules():
    """
    Get a list of all modules and submodules in the system that we can import.

    Exit:  modules: a list of modules.
    """
    with open(os.devnull, 'w') as devnull:
        modules = subprocess.Popen(
            ['python', '-c', 'help("modules")'],
            stdout=subprocess.PIPE, stderr=devnull).stdout.read()
        if not isinstance(modules, six.string_types):
            modules = modules.decode('utf8')
        submodules = subprocess.Popen(
            ['python', '-c', 'help("modules .")'],
            stdout=subprocess.PIPE, stderr=devnull).stdout.read()
        if not isinstance(submodules, six.string_types):
            submodules = submodules.decode('utf8')
    modules = modules.replace('\r\n', '\n').strip().split('\n\n')[1].split()
    submodules = submodules.replace('\r\n', '\n').strip().split('\n\n')[1].split('\n')
    submodules = [item.strip() for item in [
        item.split(' - ')[0] for item in submodules] if '.' in item]
    # This filter shouldn't remove anything
    submodules = [item for item in submodules if item.split('.')[0] in modules]
    modules = set(modules + submodules)

    # Remove modules with dashes in their names
    modules = [item for item in modules if '-' not in item]

    # Remove modules starting with values in ExcludeModules or containing a
    # module component in ExcludeParts
    regex = re.compile(
        '(^(' + '|'.join([re.escape(val) for val in ExcludeModules]) +
        ')|\.(' + '|'.join([re.escape(val) for val in ExcludeParts]) +
        '))(\.|$)')
    modules = [item for item in modules if not regex.search(item)]
    modules.sort()

    for item in modules[:]:
        try:
            # If we already imported the module based on a previous import, we
            # don't need to include it explicitly
            if item in sys.modules and '.' in item:
                modules.remove(item)
                continue
            sys.stderr.write('? %s\r' % item)
            sys.stderr.flush()
            mod = importlib.import_module(item)  # noqa
            sys.stderr.write('+ %s\n' % item)
            sys.stderr.flush()
        except BaseException:
            # If the import fails, remove the modules from the list
            modules.remove(item)
            sys.stderr.write('- %s\n' % item)
            sys.stderr.flush()
    return modules


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
    modules = list_modules()
    if pyexePath:
        head = b'    # IMPORT ALL MODULES'
        tail = b'    # END IMPORT ALL MODULES'
        data = open(pyexePath, 'rb').read()
        imports = ('\n        import '.join([''] + modules) + '\n').encode('utf8')
        data = data.split(head, 1)[0] + head + imports + tail + data.split(tail, 1)[1]
        open(pyexePath, 'wb').write(data)
    else:
        for item in modules:
            print('import %s' % item)
