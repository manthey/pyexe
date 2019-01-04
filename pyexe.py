#!/usr/bin/python

# Wrap everything in a single function to avoid polluting the global namespace
# more than necessary.
def main():  # noqa
    import ctypes
    import os
    import six
    import sys
    import warnings

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
        Write the prompt to stderr, then call raw_input without a prompt.  This
        is to try to mimic better what the python executable does.

        Enter: prompt: prompt to print to stderr.
        """
        if prompt and len(prompt):
            sys.stderr.write(prompt)
            sys.stderr.flush()
        return six.moves.input('')

    def get_env_flag(currentValue, key):
        """
        Check if the environment has a key.  Parse this as a positive integer,
        if possible, otherwise treat it like 1.  Return the greater of the
        current value and the parsed value.
        """
        if not os.environ.get(key):
            return currentValue
        try:
            value = int(os.environ.get(key))
            if value < 0:
                value = 1
        except ValueError:
            value = 1
        return max(currentValue, value)

    def print_version(details=1):
        """
        Print the current version.

        Enter: details: 0 if part of help, 1 for basic verison, 2 for more
                    details.
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

    def run_file(runFile, runFileArgv, skipFirstLine, globenv):
        """
        Exec a file with a limited set of globals.  We can't use runpy.run_path
        for (a) skipped first line, (b) Python 2.7 and zipapps (pyz files).
        Rather than use run_path in the limited cases where it can be used, we
        use one code path for executing files in general.

        Enter: runFile: path of the file to exec.
               runFileArgv: arguments to set sys.argv to.
               SkipFileLine: True to skip the first line of the file.
               globenv: global environment to use.
        """
        import codecs
        import re
        import zipfile
        sys.argv[:] = runFileArgv
        if zipfile.is_zipfile(os.path.abspath(runFile)):
            sys.path[0:0] = [runFile]
            with zipfile.ZipFile(runFile) as zptr:
                src = zptr.open('__main__.py').read()
        else:
            if not Isolated:
                sys.path[0:0] = [os.path.split(os.path.abspath(runFile))[0]]
            with open(runFile, 'rb') as fptr:
                src = fptr.read()
                # This is similar to what universal newline support does
                useenc = 'utf-8' if sys.version_info >= (3, ) else 'latin-1'
                if src.startswith(codecs.BOM_UTF8):
                    useenc = 'utf-8'
                    src = src[len(codecs.BOM_UTF8):]
                src = src.replace(b'\r\n', b'\n').replace(b'\r', b'\n')
                if skipFirstLine:
                    src = src.split(b'\n', 1)[1] if b'\n' in src else b''
                # first two lines may contain encoding:
                firsttwo = src.split(b'\n', 2)
                coding_re = re.compile(r'^[ \t\f]*#.*?coding[:=][ \t]*([-_.a-zA-Z0-9]+)')
                try:
                    match = coding_re.match(firsttwo[0].decode('utf8'))
                except Exception:
                    match = None
                if match:
                    useenc = match.group(1)
                    src = b'\n'.join(firsttwo[1:])
                else:
                    try:
                        match = coding_re.match(firsttwo[1].decode('utf8'))
                    except Exception:
                        match = None
                    if match:
                        useenc = match.group(1)
                        src = b'\n'.join(firsttwo[:1] + firsttwo[2:])
                src = src.decode(useenc)
        # If we use anything other than the actual globals() dictionary,
        # multiprocessing doesn't work.  Therefore, mutate globals() and
        # merge back in when done.
        globs = globals()
        originalGlobals = globs.copy()
        globs.clear()
        globs.update(globenv)
        globs['__name__'] = '__main__'
        globs['__file__'] = runFile
        six.exec_(src, globs)
        # globs.clear()
        globs.update(originalGlobals)

    def skip_once(cls, method):
        """
        The first time a mthod of a class is called, skip doing the action.

        Enter: cls: the class instance with the method.
               method: the name of the method (a string).
        """
        orig = getattr(cls, method, None)

        def skip(*args, **kwargs):
            setattr(cls, method, orig)

        setattr(cls, method, skip)

    if hasattr(sys, 'frozen'):
        delattr(sys, 'frozen')
    Help = False
    Interactive = None
    InteractiveArgv = None
    Isolated = False
    NoSiteFlag = False
    Optimize = 0
    PrintVersion = 0
    QuietFlag = False
    RunCommand = None
    RunFile = None
    RunModule = None
    SkipFirstLine = False
    StartupFile = None
    TabcheckFlag = 0
    Unbuffered = False
    UseEnvironment = True
    VerboseFlag = 0
    Warning3k = 0
    WarningBytes = 0
    WarningDivision = None
    WarningOptions = []
    skip = 0
    sys.dont_write_bytecode = False
    for i in six.moves.range(1, len(sys.argv)):  # noqa
        if skip:
            skip -= 1
            continue
        arg = sys.argv[i]
        if arg.startswith('-') and len(arg) > 1 and arg[1:2] != '-':
            for let in arg[1:]:
                if let == 'b':
                    WarningBytes += 1
                elif let == 'B':
                    sys.dont_write_bytecode = True
                elif let == 'c':
                    RunCommand = sys.argv[i+1+skip]
                    RunCommandArgv = ['-c'] + sys.argv[i+2+skip:]
                    skip = len(sys.argv)
                elif let == 'd':
                    # We don't have to do anything for this flag, since we
                    # never bundle with a debug build of Python
                    pass
                elif let == 'E':
                    UseEnvironment = False
                elif let == 'h':
                    Help = True
                elif let == 'i':
                    Interactive = True
                elif let == 'I' and sys.version_info >= (3, ):
                    UseEnvironment = False
                    Isolated = True
                elif let == 'm' and i+1 < len(sys.argv):
                    RunModule = sys.argv[i+1+skip]
                    RunModuleArgv = sys.argv[i+1+skip:]
                    skip = len(sys.argv)
                elif let == 'O':
                    Optimize += 1
                elif let == 'q' and sys.version_info >= (3, ):
                    QuietFlag = True
                elif let == 'Q' and sys.version_info < (3, ):
                    if arg.startswith('-' + let) and len(arg) > 2:
                        WarningDivision = arg[2:]
                    else:
                        WarningDivision = sys.argv[i+1+skip]
                        skip += 1
                    if WarningDivision not in ('old', 'warn', 'warnall', 'new'):
                        sys.stderr.write("""-Q option should be `-Qold', `-Qwarn', `-Qwarnall', or `-Qnew' only
usage: %s [option] ... [-c cmd | -m mod | file | -] [arg] ...
Try `%s -h' for more information.
    """ % (sys.argv[0], sys.argv[0]))
                        sys.exit(2)
                    if arg.startswith('-' + let) and len(arg) > 2:
                        break
                elif let == 'R':
                    # We can't change the hash seed after start, so ignore it.
                    pass
                elif let == 's':
                    # We don't have to do anything for this flag, since we
                    # never have a local user site-packages directory in
                    # stand-alone mode
                    pass
                elif let == 'S':
                    NoSiteFlag = True
                elif let == 't' and sys.version_info < (3, ):
                    TabcheckFlag += 1
                elif let == 'u':
                    Unbuffered = True
                elif let == 'v':
                    VerboseFlag += 1
                elif let == 'V':
                    PrintVersion += 1
                elif let == 'W':
                    if arg.startswith('-' + let) and len(arg) > 2:
                        WarningOptions.append(arg[2:])
                        break
                    else:
                        WarningOptions.append(sys.argv[i+1+skip])
                        skip += 1
                elif let == 'x':
                    SkipFirstLine = True
                elif let == 'X':
                    # We don't have do anything for this flag, as the basic
                    # implementation doesn't have such options.
                    if arg.startswith('-' + let) and len(arg) > 2:
                        break
                    else:
                        skip += 1
                elif let == '3' and sys.version_info < (3, ):
                    Warning3k += 1
                    TabcheckFlag = max(TabcheckFlag, 1)
                else:
                    Help = True
        elif ((arg == '--check-hash-based-pycs' or arg.startswith('--check-hash-based-pycs=')) and
              sys.version_info >= (3, 6)):
            # There is no exposure to this option in Python's DLL, so can't do
            # it
            if '=' not in arg:
                skip += 1
        elif arg == '--all':
            pass
        elif arg == '--help' or arg == '/?':
            Help = True
        elif arg == '--version':
            PrintVersion += 1
        elif arg == '-':
            Interactive = 'check'
            InteractiveArgv = ['-'] + sys.argv[i+1+skip:]
            skip = len(sys.argv)
        elif arg.startswith('-'):
            Help = True
        elif not RunFile:
            RunFile = sys.argv[i+skip]
            RunFileArgv = sys.argv[i+skip:]
            skip = len(sys.argv)
    if Help:
        print_version(0)
        print('usage: %s [option] ... [-c cmd | -m mod | file | -] [arg] ...' % sys.argv[0])
        print("""Options and arguments (and corresponding environment variables):""")
        if sys.version_info >= (3, ):
            print("""-b     : issue warnings about str(bytes_instance), str(bytearray_instance)
         and comparing bytes/bytearray with str. (-bb: issue errors)""")
        print("""-B     : don't write .py[co] files on import; also PYTHONDONTWRITEBYTECODE=x
-c cmd : program passed in as string (terminates option list)
-E     : ignore PYTHON* environment variables (such as PYTHONPATH)
-h     : print this help message and exit (also --help, /?)
-i     : inspect interactively after running script; forces a prompt even
         if stdin does not appear to be a terminal; also PYTHONINSPECT=x""")
        if sys.version_info >= (3, ):
            print("""-I     : isolate Python from the user's environment (implies -E and -s)""")
        print("""-m mod : run library module as a script (terminates option list)
-O     : optimize generated bytecode slightly; also PYTHONOPTIMIZE=x
-OO    : remove doc-strings in addition to the -O optimizations""")
        if sys.version_info >= (3, ):
            print("""-q     : don't print version and copyright messages on interactive startup""")
        if sys.version_info < (3, ):
            print("""-Q arg : division options: -Qold (default), -Qwarn, -Qwarnall, -Qnew""")
        print("""-s     : don't add user site directory to sys.path; also PYTHONNOUSERSITE
-S     : don't imply 'import site' on initialization""")
        if sys.version_info < (3, ):
            print("""-t     : issue warnings about inconsistent tab usage (-tt: issue errors)""")
        print("""-u     : unbuffered binary stdout and stderr, stdin always buffered;
         also PYTHONUNBUFFERED=x
         see man page for details on internal buffering relating to '-u'
-v     : verbose (trace import statements); also PYTHONVERBOSE=x
         can be supplied multiple times to increase verbosity
-V     : print the Python version number and exit (also --version).  Use twice
         for more complete information.
-W arg : warning control; arg is action:message:category:module:lineno
         also PYTHONWARNINGS=arg
-x     : skip first line of source, allowing use of non-Unix forms of #!cmd
-X opt : set implementation-specific option""")
        if sys.version_info < (3, ):
            print("""-3     : warn about Python 3.x incompatibilities that 2to3 cannot trivially fix""")  # noqa
        print("""file   : program read from script file
-      : program read from stdin (default; interactive mode if a tty)
arg ...: arguments passed to program in sys.argv[1:]
Stand-alone specific options:
--all  : imports all bundled modules.

Other environment variables:
PYTHONSTARTUP: file executed on interactive startup (no default)
PYTHONPATH   : ';'-separated list of directories prefixed to the
               default module search path.  The result is sys.path.
PYTHONCASEOK : ignore case in 'import' statements (Windows).""")
        sys.exit(0)
    if PrintVersion:
        print_version(PrintVersion)
        sys.exit(0)
    # Explicitly add the path of the current executable to the system paths and
    # its subpath of Lib\site-packages.  Installed Python always includes these
    # paths, but PyInstaller changes them to the expanded paths.
    sys.path[0:0] = [
        os.path.abspath(os.path.dirname(sys.executable)),
        os.path.abspath(os.path.join(os.path.dirname(sys.executable), 'Lib', 'site-packages'))
    ]
    if UseEnvironment:
        if os.environ.get('PYTHONDONTWRITEBYTECODE'):
            sys.dont_write_bytecode = True
        if Interactive is not True and os.environ.get('PYTHONINSPECT'):
            Interactive = 'check'
        Optimize = get_env_flag(Optimize, 'PYTHONOPTIMIZE')
        if os.environ.get('PYTHONPATH'):
            sys.path[0:0] = os.environ.get('PYTHONPATH').split(os.pathsep)
        StartupFile = os.environ.get('PYTHONSTARTUP')
        if Unbuffered is False and os.environ.get('PYTHONUNBUFFERED'):
            Unbuffered = True
        VerboseFlag = get_env_flag(VerboseFlag, 'PYTHONVERBOSE')
        if os.environ.get('PYTHONWARNINGS'):
            WarningOptions.extend(os.environ.get('PYTHONWARNINGS').split(','))
    if Isolated:
        # We have to suppress some environment effects
        os.environ.pop('PYTHONCASEOK', None)
        for key in list(sys.modules):  # for Python 3.x
            if hasattr(sys.modules[key], '_relax_case'):
                sys.modules[key]._relax_case = lambda: False
    if VerboseFlag:
        ctypes.c_int.in_dll(ctypes.pythonapi, 'Py_VerboseFlag').value = VerboseFlag
    if TabcheckFlag:
        ctypes.c_int.in_dll(ctypes.pythonapi, 'Py_TabcheckFlag').value = TabcheckFlag
    if Warning3k:
        ctypes.c_int.in_dll(ctypes.pythonapi, 'Py_Py3kWarningFlag').value = Warning3k
    if Optimize:
        ctypes.c_int.in_dll(ctypes.pythonapi, 'Py_OptimizeFlag').value = Optimize
    if WarningBytes:
        for idx, f in enumerate(warnings.filters):
            if f[2] == BytesWarning:
                warnings.filters[idx] = tuple(
                    ['default' if WarningBytes == 1 else 'error'] + list(f)[1:])
        if not any([f for f in warnings.filters if f[2] == BytesWarning]):
            warnings.filterwarnings(
                'default' if WarningBytes == 1 else 'error', category=BytesWarning)
        ctypes.c_int.in_dll(ctypes.pythonapi, 'Py_BytesWarningFlag').value = WarningBytes
    if WarningDivision == 'new':
        ctypes.c_int.in_dll(ctypes.pythonapi, '_Py_QnewFlag').value = 1
    elif WarningDivision in ('warn', 'warnall') or Warning3k:
        ctypes.c_int.in_dll(ctypes.pythonapi, 'Py_DivisionWarningFlag').value = (
            2 if WarningDivision == 'warnall' else 1)
        warnings.filterwarnings('default', category=DeprecationWarning,
                                message='classic [a-z]+ division')
    if Warning3k:
        warnings.filterwarnings('default', category=DeprecationWarning)
    sys.warnoptions[0:0] = WarningOptions
    warnings._processoptions(WarningOptions)
    bufsize = 1 if sys.version_info >= (3, ) else 0
    if Unbuffered:
        sys.stdin = os.fdopen(sys.stdin.fileno(), 'r', bufsize)
        sys.stdout = os.fdopen(sys.stdout.fileno(), 'a+', bufsize)
        sys.stderr = os.fdopen(sys.stderr.fileno(), 'a+', bufsize)
    if not NoSiteFlag:
        import site
        site.main()
    # Generate the globals/locals environment
    globenv = {}
    for key in list(globals().keys()):
        if key.startswith('_') and key != '_frozen_name':
            globenv[key] = globals()[key]
    if RunFile:
        run_file(RunFile, RunFileArgv, SkipFirstLine, globenv)
    elif RunModule:
        import runpy
        sys.argv[:] = RunModuleArgv
        runpy.run_module(RunModule, run_name='__main__')
    elif RunCommand is not None:
        if not Isolated:
            sys.path[0:0] = ['']
        sys.argv[:] = RunCommandArgv
        six.exec_(RunCommand, globenv)
    elif Interactive is None:
        Interactive = 'check'
    if Interactive:
        if not Isolated:
            sys.path[0:0] = ['']
        if InteractiveArgv:
            sys.argv[:] = InteractiveArgv
        if Interactive is True or sys.stdin.isatty():
            if not RunFile and not RunModule and not RunCommand and StartupFile:
                import runpy
                runpy.run_path(StartupFile, run_name='__main__')
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
            if RunModule or RunCommand or QuietFlag:
                banner = ''
                if sys.version_info < (3, ):
                    skip_once(cons, 'write')
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


main()
