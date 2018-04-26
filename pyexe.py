#!/usr/bin/python

import os
import six
import sys

AllModules = False

if len(sys.argv) == 1 and not hasattr(sys, 'frozen'):
    AllModules = True
if not AllModules and sys.argv[:2][-1] != '--all':
    pass
else:
    # IMPORT ALL MODULES
    import modules_pyexe_list  # noqa, this is the output of modules_pyexe
    print(dir(modules_pyexe_list))  # for installers to include submodules
    # END IMPORT ALL MODULES
    # Import modules which failed to be included in the auto-generated list.
    import setuptools._vendor.pyparsing  # noqa


def alternate_raw_input(prompt=None):
    """
    Write the prompt to stderr, then call raw_input without a prompt.  This is
    to try to mimic better what the python executable does.

    Enter: prompt: prompt to print to stderr.
    """
    if prompt and len(prompt):
        sys.stderr.write(prompt)
        sys.stderr.flush()
    return six.moves.input('')


def print_version(details=1):
    """
    Print the current version.

    Enter: details: 0 if part of help, 1 for basic verison, 2 for more details.
    """
    from py_version import Version, Description

    print('%s, Version %s' % (Description, Version))
    if details > 1:
        print('Python %s' % (sys.version))
        # pywin32
        import win32api
        fileinfo = win32api.GetFileVersionInfo(win32api.__file__, '\\')
        print('pywin32: %s' % str(fileinfo['FileVersionLS'] >> 16))
        # Others
        import importlib
        for module_name in ('pip', 'psutil', 'setuptools', 'six'):
            module = importlib.import_module(module_name)
            print('%s: %s' % (module_name, module.__version__))


if hasattr(sys, 'frozen'):
    delattr(sys, 'frozen')
Help = False
NoSiteFlag = False
Interactive = None
InteractiveArgv = None
PrintVersion = 0
RunCommand = None
RunModule = None
SkipFirstLine = False
Start = None
Unbuffered = False
UseEnvironment = True
skip = 0
for i in six.moves.range(1, len(sys.argv)):  # noqa
    if skip:
        skip -= 1
        continue
    arg = sys.argv[i]
    if arg.startswith('-') and len(arg) > 1 and arg[1:2] != '-':
        for let in arg[1:]:
            if let == 'c':
                RunCommand = sys.argv[i+1+skip]
                RunCommandArgv = ['-c'] + sys.argv[i+2+skip:]
                skip = len(sys.argv)
            elif let == 'E':
                UseEnvironment = False
            elif let == 'h':
                Help = True
            elif let == 'i':
                Interactive = True
            elif let == 'm' and i+1 < len(sys.argv):
                RunModule = sys.argv[i+1+skip]
                RunModuleArgv = sys.argv[i+1+skip:]
                skip = len(sys.argv)
                break
            elif let == 'S':
                NoSiteFlag = True
            elif let == 'u':
                Unbuffered = True
            elif let == 'V':
                PrintVersion += 1
            elif let == 'x':
                SkipFirstLine = True
            elif let in ('b', 'B', 'd', 'I', 'O', 'q', 's', 'v'):
                # ignore these options
                pass
            elif let in ('W', 'X'):
                # ignore these options
                skip += 1
                pass
            else:
                Help = True
    elif arg == '--check-hash-based-pycs':
        # ignore this option
        skip += 1
        pass
    elif arg == '--all':
        continue
    elif arg == '--help' or arg == '/?':
        Help = True
    elif arg == '--version':
        PrintVersion += 1
    elif arg == '-':
        Interactive = 'check'
        InteractiveArgv = ['-'] + sys.argv[i+1+skip:]
        skip = len(sys.argv)
        break
    elif arg.startswith('-'):
        Help = True
    elif not Start:
        Start = i + skip
        break
if Help:
    print_version(0)
    print('usage: %s [option] ... [-c cmd | -m mod | file | -] [arg] ...' % sys.argv[0])
    print("""Stand-alone specific options:
--all attempts to import all modules.
General Python options and arguments (and corresponding environment variables):
-c runs the remaining options as a program.
-E ignores environment variables.
-i forces a prompt even if stdin does not appear to be a terminal; also
  PYTHONINSPECT=x
--help, -h, or /? prints this message.
-m runs the specified python module.
-S supresses importing the site module
-u runs in unbuffered mode; also PYTHONUNBUFFERED=x
-V prints the version and exits (--version also works).
-x skips the first line of a source file.
If no file is specified and stdin is a terminal, the interactive interpreter is
  started.""")
    sys.exit(0)
if PrintVersion:
    print_version(PrintVersion)
    sys.exit(0)
if Interactive is not True and UseEnvironment:
    if os.environ.get('PYTHONINSPECT'):
        Interactive = 'check'
if Unbuffered is False and UseEnvironment:
    if os.environ.get('PYTHONUNBUFFERED'):
        Unbuffered = True
bufsize = 1 if sys.version_info >= (3, ) else 0
if Unbuffered:
    sys.stdin = os.fdopen(sys.stdin.fileno(), 'r', bufsize)
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'a+', bufsize)
    sys.stderr = os.fdopen(sys.stderr.fileno(), 'a+', bufsize)
globenv = {}
if not NoSiteFlag:
    import site
    site.main()
# Generate the globals/locals environment
for key in list(globals().keys()):
    if key.startswith('_'):
        globenv[key] = globals()[key]
if Start:  # noqa
    import zipfile
    sys.argv[:] = sys.argv[Start:]
    __name__ = '__main__'
    __file__ = sys.argv[0]
    if zipfile.is_zipfile(__file__):
        sys.path[0:0] = [__file__]
        with zipfile.ZipFile(__file__) as zptr:
            src = zptr.open('__main__.py').read()
    else:
        sys.path[0:0] = [os.path.split(__file__)[0]]
        with open(__file__) as fptr:
            if SkipFirstLine:
                discard = fptr.readline()
            src = fptr.read()
    # If we use the simplified global dictionary, multiprocessing doesn't work
    # (this should be investigated further)
    six.exec_(src)
elif RunModule:
    import runpy
    sys.argv[:] = RunModuleArgv
    runpy.run_module(RunModule, run_name='__main__')
elif RunCommand is not None:
    sys.path[0:0] = ['']
    sys.argv[:] = RunCommandArgv
    six.exec_(RunCommand, globenv)
elif Interactive is None:
    Interactive = 'check'
if Interactive:
    sys.path[0:0] = ['']
    if InteractiveArgv:
        sys.argv[:] = InteractiveArgv
    if Interactive is True or sys.stdin.isatty():
        import code
        cons = code.InteractiveConsole(locals=globenv)
        if not sys.stdout.isatty():
            cons.raw_input = alternate_raw_input
            if not Unbuffered:
                sys.stdout = os.fdopen(sys.stdout.fileno(), 'a+', bufsize)
                sys.stderr = os.fdopen(sys.stderr.fileno(), 'a+', bufsize)
        banner = 'Python %s' % sys.version
        if not NoSiteFlag:
            banner += '\nType "help", "copyright", "credits" or "license" for more information.'
        if RunModule or RunCommand:
            banner = ''
        kwargs = {}
        if sys.version_info >= (3, 6):
            kwargs['exitmsg'] = ''
        cons.interact(banner=banner, **kwargs)
    else:
        src = sys.stdin.read()
        # This doesn't work the way I expect for some reason
        #  interp = code.InteractiveInterpreter(locals=globenv)
        #  interp.runsource(src, '<stdin>')
        # But an exec works fine
        globenv['__file__'] = '<stdin>'
        six.exec_(src, globenv)
