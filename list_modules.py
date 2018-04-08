#!/usr/bin/python

import importlib
import os
import sys

modules = os.popen("""python -c "help('modules')" 2>&1""").read()
modules = modules.replace('\r\n', '\n').strip().split('\n\n')[1].split()
modules.sort()

submodules = os.popen("""python -c "help('modules .')" 2>&1""").read()
submodules = submodules.replace('\r\n', '\n').strip().split('\n\n')[1].split('\n')
submodules = [item.strip() for item in [item.split(' - ')[0] for item in submodules] if '.' in item]
# This filter shouldn't remove anything
submodules = [item for item in submodules if item.split('.')[0] in modules]
submodules.sort()
all = modules[:]
all.extend(submodules)
all.sort()

# Remove modules with dashes in their names
all = [item for item in all if '-' not in item]

# Modules we know we can't work with or are completely pointless
Exclude = [
    # our own code
    'py', 'pymodules',
    # installers
    'py2exe',
    'PyInstaller', 'pefile', 'macholib', 'dis3', 'future', 'altgraph',
    'ordlookup', 'peutils', 'libfuturize', 'libpasteurize', 'past',
    # Pointless modules
    'antigravity', 'this', 'lib2to3.__main__', 'unittest.__main__',
    'win32com.demos', 'win32com.directsound.test', 'win32com.test',
    'win32traceutil',
    # Much of win32com is really located in win32comext.  py2exe doesn't attach
    # this properly, and I haven't gotten the work-around working.
    'win32com.adsi', 'win32com.adsi.adsicon', 'win32com.authorization',
    'win32com.authorization.authorization', 'win32com.axcontrol',
    'win32com.axcontrol.axcontrol', 'win32com.axdebug',
    'win32com.axdebug.debugger', 'win32com.axdebug.dump',
    'win32com.axscript.asputil', 'win32com.axscript.client',
    'win32com.axscript.client.debug', 'win32com.axscript.client.pydumper',
    'win32com.axscript.client.pyscript_rexec', 'win32com.axscript.server',
    'win32com.axscript.server.axsite', 'win32com.axscript.server.error',
    'win32com.bits', 'win32com.bits.bits', 'win32com.directsound',
    'win32com.directsound.directsound', 'win32com.ifilter',
    'win32com.ifilter.ifilter', 'win32com.ifilter.ifiltercon',
    'win32com.internet', 'win32com.internet.inetcon',
    'win32com.internet.internet', 'win32com.mapi', 'win32com.mapi.emsabtags',
    'win32com.mapi.exchange', 'win32com.mapi.exchdapi', 'win32com.mapi.mapi',
    'win32com.mapi.mapiutil', 'win32com.propsys', 'win32com.propsys.pscon',
    'win32com.shell', 'win32com.shell.shell', 'win32com.shell.shellcon',
    'win32com.taskscheduler', 'win32com.taskscheduler.taskscheduler',
    # These require additional dlls
    'win32ui', 'win32uiole',
    # These require win32ui
    'pywin.debugger', 'pywin.dialogs', 'pywin.docking', 'pywin.framework',
    'pywin.mfc', 'pywin.scintilla', 'pywin.tools', 'win32com.client.combrowse',
    'win32com.client.tlbrowse',
    # Linux only
    'pty', 'tty',
    # Tests
    'bsddb.test', 'ctypes.test', 'distutils.tests', 'email.test', 'json.tests',
    'lib2to3.tests', 'sqlite3.test', 'test', 'unittest.test', 'psutil.tests',
    # Modules in appveyor that shouldn't be included, plus tkinter
    'Canvas', 'Dialog', 'FileDialog', 'FixTk', 'ScrolledText', 'SimpleDialog',
    'Tix', 'Tkconstants', 'Tkdnd', 'Tkinter', '_LWPCookieJar',
    '_MozillaCookieJar' '_markupbase', '_tkinter', 'adodbapi', 'altgraph',
    'curses', 'dde', 'idlelib', 'tkColorChooser', 'tkCommonDialog',
    'tkFileDialog', 'tkFont', 'tkMessageBox', 'tkSimpleDialog', 'tkinter',
    'ttk', 'turtle', 'turtledemo', 'tcl', 'tk', 'Tkinter',
]
for item in all[:]:
    if item in Exclude:
        all.remove(item)
        continue
    for ex in Exclude:
        if item.startswith(ex+'.'):
            all.remove(item)
            break
for item in all[:]:
    try:
        # sys.stderr.write('?- %s --\n' % item)
        # sys.stderr.flush()
        if item in sys.modules and '.' in item:
            all.remove(item)
            continue
        mod = importlib.import_module(item)
        sys.stderr.write('-- %s --\n' % item)
        sys.stderr.flush()
    except BaseException:
        all.remove(item)

if len(sys.argv) > 1:
    head = b'    # IMPORT ALL MODULES'
    tail = b'    # END IMPORT ALL MODULES'
    data = open(sys.argv[1], 'rb').read()
    imports = ('\n    import '.join([''] + all) + '\n').encode('utf8')
    data = data.split(head)[0] + head + imports + tail + data.split(tail)[1]
    open(sys.argv[1], 'wb').write(data)
else:
    for item in all:
        print('import %s' % item)
