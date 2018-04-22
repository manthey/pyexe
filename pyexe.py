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


def alternate_raw_input(prompt=None):
    """
    Write the prompt to stderr, then call raw_input without a prompt.  This is
    to try to mimic better what the python executable does.

    Enter: prompt: prompt to print to stderr.
    """
    if prompt and len(prompt):
        sys.stderr.write(prompt)
        sys.stderr.flush()
    return raw_input('')


def print_version(details=1):
    """
    Print the current version.

    Enter: details: if 2, print more details.
    """
    from py_version import Version, Description

    print('%s, Version %s' % (Description, Version))
    if details > 1:
        print('Python %s' % (sys.version))
        import importlib
        # pywin32
        import win32api
        fileinfo = win32api.GetFileVersionInfo(win32api.__file__, '\\')
        print('pywin32: %s' % str(fileinfo['FileVersionLS'] >> 16))
        for module_name in ('pip', 'psutil', 'setuptools', 'six'):
            module = importlib.import_module(module_name)
            print('%s: %s' % (module_name, module.__version__))


if hasattr(sys, 'frozen'):
    delattr(sys, 'frozen')
Help = False
DirectCmd = None
ImportSite = True
Interactive = 'check'
PrintVersion = 0
RunModule = False
SkipFirstLine = False
Start = None
Unbuffered = False
UseEnvironment = True
skip = 0
for i in six.moves.range(1, len(sys.argv)):  # noqa
    if DirectCmd is not None:
        break
    if skip:
        skip -= 1
        continue
    arg = sys.argv[i]
    if arg.startswith('-') and arg[1:2] != '-':
        for let in arg[1:]:
            if let == 'c':
                DirectCmd = sys.argv[i+1+skip]
                DirectArgv = ['-c'] + sys.argv[i+2+skip:]
                skip = len(sys.argv)
            elif let == 'E':
                UseEnvironment = False
            elif let == 'i':
                Interactive = True
            elif let == 'm' and i+1 < len(sys.argv):
                RunModule = sys.argv[i+1+skip]
                RunArgv = sys.argv[i+1+skip:]
                skip = len(sys.argv)
                break
            elif let == 'S':
                ImportSite = False
            elif let == 'u':
                Unbuffered = True
            elif let == 'V':
                PrintVersion += 1
            elif let == 'x':
                SkipFirstLine = True
            elif let in ('B', 'E', 'O', 's'):
                # ignore these options
                pass
            else:
                Help = True
    elif arg == '--all':
        continue
    elif arg == '--help' or arg == '-h' or arg == '/?':
        Help = True
    elif arg == '--version':
        PrintVersion += 1
    elif arg.startswith('-'):
        Help = True
    elif not Start:
        Start = i
        break
if Help:
    from py_version import Version, Description
    print('%s, Version %s' % (Description, Version))
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
    print(repr(sys.argv))
    sys.exit(0)
if PrintVersion:
    print_version(PrintVersion)
    sys.exit(0)
if Interactive == 'check' and UseEnvironment:
    if os.environ.get('PYTHONINSPECT'):
        Interactive = True
if Unbuffered is False and UseEnvironment:
    if os.environ.get('PYTHONUNBUFFERED'):
        Unbuffered = True
if Unbuffered:
    bufsize = 1 if sys.version_info >= (3, ) else 0
    sys.stdin = os.fdopen(sys.stdin.fileno(), 'r', bufsize)
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'a+', bufsize)
    sys.stderr = os.fdopen(sys.stderr.fileno(), 'a+', bufsize)
globenv = {}
if ImportSite:
    import site
    site.main()
# Generate the globals/locals environment
for key in list(globals().keys()):
    if key.startswith('_'):  # or key == 'AllModules':
        globenv[key] = globals()[key]
if Start:  # noqa
    sys.argv[:] = sys.argv[Start:]
    __name__ = '__main__'
    __file__ = sys.argv[0]
    sys.path[0:0] = [os.path.split(__file__)[0]]
    with open(sys.argv[0]) as fptr:
        if SkipFirstLine:
            discard = fptr.readline()
        src = fptr.read()
        # If we the simplified global dictionary, multiprocessing doesn't work
        six.exec_(src)
elif RunModule:
    import runpy
    sys.argv[:] = RunArgv
    runpy.run_module(RunModule, run_name='__main__')
elif DirectCmd:
    sys.path[0:0] = ['']
    sys.argv[:] = DirectArgv
    six.exec_(DirectCmd, globenv)
else:
    if Interactive == 'check':
        Interactive = sys.stdin.isatty()
    sys.path[0:0] = ['']
    if Interactive:
        import code
        cons = code.InteractiveConsole(locals=globenv)
        if not sys.stdout.isatty():
            cons.raw_input = alternate_raw_input
            if not Unbuffered:
                sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
                sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', 0)
        cons.interact()
    elif False:
        # This will run code as it comes it, rather than wait until it has
        # parsed it all; it doesn't seem to be what the main python interpreter
        # ever does, however.
        import code
        interp = code.InteractiveInterpreter(locals=globenv)
        src = []
        for line in sys.stdin:
            if not len(line.rstrip('\r\n')):
                continue
            if line.startswith('#'):
                continue
            if line.rstrip('\r\n')[0:1] not in (' ', '\t'):
                if len(src):
                    interp.runsource(''.join(src), '<stdin>')
                    src = []
            src.append(line)
        if len(src):
            interp.runsource(''.join(src))
    elif not Start:
        src = sys.stdin.read()
        # This doesn't work the way I expect for some reason
        #  interp = code.InteractiveInterpreter(locals=globenv)
        #  interp.runsource(src, '<stdin>')
        # But an exec works fine
        six.exec_(src, globenv)
