#!/usr/bin/python
#
# This is a small stub that is intended to be built into an executable with a
# setup.py file using "python setup.py py2exe".  This results in an executable
# called py.exe.  This can be used to run an arbitrary python script on Windows
# (XP and later) via py.exe (name of script).
#
# Changes:
#  2.7.4.1:
#   * initial release
#  2.7.4.2:
#   * fixed an issue with __file__ and __name__
#  2.7.4.3:
#   * Added the program path to sys.path when running a program, and '' to
# sys.path when running direct or interpretted.
#  2.7.5.4:
#   * Upgraded to python 2.7.5
#  2.7.5.5:
#   * Imported submodules, such as logging.handlers, since they weren't
# included implicitly.
#  2.7.8.6:
#   * Added support for multiprocessing forking
#   * Added support for non-ttty direct usage (input and output pipes, for
# instance)
#   * Added support for -i option and PYTHONINSPECT environment variable.
#   * Turned off 'frozen' flag in py.exe
#   * Upgraded pywin32 to build 219 (was 218).
#   * Upgraded to python 2.7.8
#   * Added import site to interactive prompts to get help and other commands
# added to the builtins.
#   * Added support for unbuffered -u option and PYTHONUNBUFFERED environment
# variable.
#  2.7.8.7:
#   * Added support for -E, -x, and --version options.
#   * Changed how the globals / locals dictionaries are used for greater
# consistency in different execution modes.
#   * Accept multiple single letter command line options grouped together.
#  2.7.8.8:
#   * Fixed a bug I introduced in the last version when renaming the variable
# 'loc'.
#  2.7.8.9:
#   * My change to make globals dictionaries more consistent broke
# multiprocessing forking.  I've reverted some of the changes.
#  2.7.9.10:
#   * Upgraded to python 2.7.9
#   * Added psutil 2.1.3 win32
#   * Added support for the -m option.
#   * Turned off the optimization flag when building py.exe.  Having it on
# interferes with some modules (such as sympy) which rely on docstring
# manipulation.

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
    import pymodules  # noqa
    print(dir(pymodules))  # for installers to include submodules
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


if hasattr(sys, 'frozen'):
    delattr(sys, 'frozen')
Help = False
DirectCmd = None
ImportSite = True
Interactive = 'check'
RunModule = False
ShowVersion = False
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
                DirectCmd = ' '.join(sys.argv[i+1+skip:])
                DirectCmd = sys.argv[i+1+skip:]
            elif let == 'E':
                UseEnvironment = False
            elif let == 'i':
                Interactive = True
            elif let == 'm' and i+1 < len(sys.argv):
                RunModule = sys.argv[i+1]
                skip = 1
            elif let == 'S':
                ImportSite = False
            elif let == 'u':
                Unbuffered = True
            elif let == 'V':
                ShowVersion = True
            elif let == 'x':
                SkipFirstLine = True
            elif let in ('E', 'O'):
                # ignore these options
                pass
            else:
                Help = True
    elif arg == '--all':
        continue
    elif arg == '--help' or arg == '-h' or arg == '/?':
        Help = True
    elif arg == '--multiprocessing-fork':
        skip = 1
        import multiprocessing.forking
        multiprocessing.forking.freeze_support()
    elif arg == '--version':
        ShowVersion = True
    elif arg.startswith('-'):
        Help = True
    elif not Start:
        Start = i
        break
if Help:
    print("""Stand-Alone Python Interpreter

Syntax: py.exe [--all] [--help] [-c (cmd) | -m (module) | (python file) [arg]]
                    [-i] [-S] [-u] [-V] [-x]
                    [--multiprocessing-fork (handle)]

--all attempts to import all modules.
-c runs the remaining options as a program.
-E ignores environment variables.
-i forces a prompt even if stdin does not appear to be a terminal; also
  PYTHONINSPECT=x
--help, -h, or /? prints this message.
-m runs the specified python module.
--multiprocessing-fork supports the multiprocessing module.
-S supresses importing the site module
-u runs in unbuffered mode; also PYTHONUNBUFFERED=x
-V prints the version and exits (--version also works).
-x skips the first line of a source file.
If no file is specified and stdin is a terminal, the interactive interpreter is
  started.""")
    # print sys.argv, repr(sys.argv)
    sys.exit(0)
if ShowVersion:
    from py_version import Version, Description
    print('%s, Version %s' % (Description, Version))
    sys.exit(0)
if Interactive == 'check' and UseEnvironment:
    if os.environ.get('PYTHONINSPECT'):
        Interactive = True
if Unbuffered is False and UseEnvironment:
    if os.environ.get('PYTHONUNBUFFERED'):
        Unbuffered = True
if Unbuffered:
    sys.stdin = os.fdopen(sys.stdin.fileno(), 'r', 0)
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
    sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', 0)
if ImportSite:
    import site  # noqa
# Generate the globals/locals environment
globenv = {}
for key in list(globals().keys()):
    if key.startswith('_'):  # or key == 'AllModules':
        globenv[key] = globals()[key]
if Start:  # noqa
    sys.argv = sys.argv[Start:]
    __name__ = '__main__'
    __file__ = sys.argv[0]
    sys.path[0:0] = [os.path.split(__file__)[0]]
    # If I try to use the simplified global dictionary, multiprocessing doesn't
    # work.
    if not SkipFirstLine:
        # execfile(sys.argv[0], globenv)
        # execfile(sys.argv[0])
        src = open(sys.argv[0]).read()
    else:
        fptr = open(sys.argv[0])
        discard = fptr.readline()
        src = fptr.read()
        fptr.close()
        # exec src in globenv
        # exec src
    six.exec_(src)
elif RunModule:
    import runpy
    runpy.run_module(RunModule, run_name='__main__')
elif DirectCmd:
    sys.path[0:0] = ['']
    sys.argv = DirectCmd
    six.exec_(DirectCmd[0], globenv)
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
    else:
        src = sys.stdin.read()
        # This doesn't work the way I expect for some reason
        #  interp = code.InteractiveInterpreter(locals=globenv)
        #  interp.runsource(src, '<stdin>')
        # But an exec works fine
        six.exec_(src, globenv)
