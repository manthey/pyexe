import contextlib
import os
import re
import shutil
import subprocess
import sys
import threading
import time

import pytest


@pytest.fixture
def exepath(request):
    return request.config.getoption('--exe')


@pytest.fixture
def pyversion(exepath):
    out, err = runPyExe(exepath, ['-VV'])
    # The -VV output includes a line like 'Python 3.14.2 ...' with the
    # version of the bundled python.
    match = re.search(r'^Python (\d+(?:\.\d+)*)', (out + err), re.MULTILINE)
    assert match, 'No python version found in the -VV output: %r' % (out + err)
    return tuple(int(part) for part in match.group(1).split('.'))


@pytest.fixture
def haspywin32(exepath):
    out, err = runPyExe(exepath, ['-c', 'import win32api'])
    return 'ModuleNotFoundError' not in (out + err)


@pytest.fixture
def haspsutil(exepath):
    out, err = runPyExe(exepath, ['-c', 'import psutil'])
    return 'ModuleNotFoundError' not in (out + err)


def runPyExe(exepath, options=None, input=None, env=None):
    """
    Run the specified exe with command line options, an option input to stdin,
    and with a modified environment.

    Enter: exepath: the fixture parameter.
           options: command line options to pass to the executable.
           input: data to pass via stdin.
           env: additional environment parameters.
    Exit:  out: stdout from the process.
           err: stderr from the process.
    """
    if options is None:
        options = []
    if env is None:
        env = {}
    cmd = [exepath] + options
    cmdenv = os.environ.copy()
    cmdenv.update(env)
    proc = subprocess.Popen(
        cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, env=cmdenv)
    if input and bytes is not str:
        input = input.encode('utf8')
    out, err = proc.communicate(input)
    if bytes is not str:
        out = out.decode('utf8')
        err = err.decode('utf8')
    return out, err


def runPyExeLines(exepath, options=None, input=None, env=None):
    """
    Run the specified exe with command line options, an option input to stdin,
    and with a modified environment.  Return line-by-line results with
    timestamps.

    Enter: exepath: the fixture parameter.
           options: command line options to pass to the executable.
           input: data to pass via stdin.
           env: additional environment parameters.
    Exit:  out: a list of (time, string) values from stdout.
           err: a list of (time, string) values from stderr.
    """
    if options is None:
        options = []
    if env is None:
        env = {}

    def readerthread(fh, buffer):
        buffer.append([])
        while True:
            data = fh.readline()
            if data is None or not len(data):
                break
            buffer[0].append((time.time(), data))
        fh.close()

    cmd = [exepath] + options
    cmdenv = os.environ.copy()
    cmdenv.update(env)
    proc = subprocess.Popen(
        cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, env=cmdenv)
    proc._readerthread = readerthread
    out, err = proc.communicate(input)
    return out, err


def runPyExeWithoutStdHandles(exepath, options=None, provide=None):
    """
    Run the specified exe when the parent process supplies only the listed
    standard handles, leaving the remaining standard handles invalid, as when
    the executable is started by a process that does not set up all of the
    standard streams (such as an older popen2-style parent).

    Enter: exepath: the fixture parameter.
           options: command line options to pass to the executable.
           provide: which of 'stdin', 'stdout', and 'stderr' to supply.
    Exit:  returncode: the exit code of the process.
           out: stdout from the process, or None if it was not supplied.
           err: stderr from the process, or None if it was not supplied.
    """
    if options is None:
        options = []
    if provide is None:
        provide = []
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESTDHANDLES
    proc = subprocess.Popen(
        [exepath] + options,
        stdin=subprocess.PIPE if 'stdin' in provide else None,
        stdout=subprocess.PIPE if 'stdout' in provide else None,
        stderr=subprocess.PIPE if 'stderr' in provide else None,
        startupinfo=startupinfo)
    out, err = proc.communicate()
    return proc.returncode, out, err


def runPyExePopen2(exepath, options=None, commands=()):
    """
    Run the specified exe driven interactively through open pipes, in the
    manner of popen2: the parent keeps the stdin pipe open, writes commands,
    and reads the responses, and never sends an end-of-file until the child
    exits.  This is how, for instance, octave's popen2 drives the
    stand-alone interpreter.

    Enter: exepath: the fixture parameter.
           options: command line options to pass to the executable.
           commands: a list of lines of input to write to stdin, with the
               last one expected to make the executable exit.
    Exit:  returncode: the exit code of the process.
           out: stdout from the process.
           err: stderr from the process.
    """
    if options is None:
        options = []
    proc = subprocess.Popen(
        [exepath] + options, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    out = []
    err = []

    def reader(fh, sink):
        while True:
            data = fh.readline()
            if not len(data):
                break
            sink.append(data)
        fh.close()

    threads = [
        threading.Thread(target=reader, args=(fh, sink))
        for fh, sink in ((proc.stdout, out), (proc.stderr, err))]
    for thread in threads:
        thread.daemon = True
        thread.start()
    for command in commands:
        proc.stdin.write(command.encode('utf8'))
        proc.stdin.flush()
        time.sleep(0.5)
    proc.stdin.close()
    proc.wait(timeout=30)
    for thread in threads:
        thread.join(timeout=30)
    return proc.returncode, b''.join(out).decode('utf8'), \
        b''.join(err).decode('utf8')


def clearPyc(basename):
    """
    Clear local pyc/pyo files based on a python filename.

    Enter: basename: the name of the python file including the .py extension.
    Exit:  count: the number of files removed.
    """
    count = 0
    for root in ('.', '__pycache__'):
        if os.path.exists(root):
            for filename in os.listdir(root):
                if (filename.startswith(os.path.splitext(basename)[0] + '.') and
                        (filename.endswith(('.pyc', '.pyo')))):
                    os.unlink(os.path.join(root, filename))
                    count += 1
    return count


@pytest.mark.pyexe
def testVersion(exepath, haspywin32, haspsutil):
    out, err = runPyExe(exepath, ['--version'])
    assert out.startswith('Stand-Alone Python Interpreter')
    match = re.match(r'Stand-Alone Python Interpreter, Version (\S+)', out)
    assert match, 'Bad version report: %r' % (out + err)
    # The version is generated by setuptools_scm from the git tags (vA.B.C
    # form); only a source run without setuptools_scm reports 'unknown'.
    assert re.match(r'v\d', match.group(1)) or match.group(1) == 'unknown'
    out, err = runPyExe(exepath, ['-V'])
    assert out.startswith('Stand-Alone Python Interpreter')
    assert 'psutil' not in out
    out, err = runPyExe(exepath, ['-V', '-V'])
    if haspsutil:
        assert 'psutil' in out
    if haspywin32:
        assert 'pywin32' in out
    out, err = runPyExe(exepath, ['-VV'])
    if haspsutil:
        assert 'psutil' in out
    if haspywin32:
        assert 'pywin32' in out


@pytest.mark.pyexe
def testHelp(exepath):
    for opt in ('--help', '-h', '-?', '/?'):
        out, err = runPyExe(exepath, [opt])
        assert 'Stand-alone specific options' in out


@pytest.mark.pyexe
def testAllFlag(exepath, haspsutil):
    out, err = runPyExe(exepath, ['--all', '-c', 'import sys;print(sorted(sys.modules.keys()))'])
    if haspsutil:
        assert 'psutil' in out
    assert 'multiprocessing' in out


def testDirectCommand(exepath):
    out, err = runPyExe(exepath, ['-c', 'print("This is a test")'])
    assert out.startswith('This is a test')


def testDirectCommandImport(exepath):
    out, err = runPyExe(exepath, [
        '-c', """import json;print(json.dumps({'test':'value'}))"""])
    assert out.startswith('{"test": "value"}')


def testImportPsutil(exepath, haspsutil):
    if not haspsutil:
        import pytest
        pytest.skip('psutil is not bundled (free-threaded builds)')
    out, err = runPyExe(exepath, [
        '-c', """import psutil;print(repr(psutil.cpu_times()))"""])
    assert 'scputimes' in out
    out, err = runPyExe(exepath, [
        '-c', """import psutil;print(repr(psutil.net_connections()))"""])
    assert 'raddr' in out


def testImportPywin32(exepath, haspywin32):
    if not haspywin32:
        import pytest
        pytest.skip('pywin32 is not bundled (free-threaded builds)')
    out, err = runPyExe(exepath, input="""import win32con
import win32file
print('%r' % [
  win32file.GetFileAttributes('.'), win32con.FILE_ATTRIBUTE_DIRECTORY])
""")
    assert '16, 16' in out


def testSiteValues(exepath, pyversion):
    for key in ('quit', 'exit', 'help', 'copyright', 'credits', 'license'):
        out, err = runPyExe(exepath, input="""try:
  print(%s)
except Exception:
  pass
""" % key)
        assert key in out.lower() or 'python.org' in out
    out, err = runPyExe(exepath, ['-S'], input='print(quit)')
    assert 'quit' not in out
    assert 'is not defined' in err


def testMultiprocessing(exepath):
    out, err = runPyExe(exepath, ['sample_multiprocessing.py'])
    assert re.search(r'Difference: \(-?0\)', out)


def testPySerialFromPip(exepath):
    with pipInstalled(exepath, 'pyserial', 'Successfully installed pyserial'):
        out, err = runPyExe(exepath, input="""import serial
ports = []
for port in range(1, 50):
  try:
    ports.append(serial.Serial('COM%d' % port))
  except Exception:
    pass
print('%r' % ports)
""")
        assert 'COM' in out or '[]' in out


def testSympyFromPip(exepath):
    with pipInstalled(exepath, 'sympy', 'Successfully installed'):
        out, err = runPyExe(exepath, input="""import sympy
x = sympy.Symbol('x')
result = sympy.simplify(1/x + (x*sympy.sin(x) - 1)/x)
print(result)
""")
        assert 'sin(x)' in out


def testRequestsPip(exepath):
    with pipInstalled(exepath, 'requests', 'Successfully installed'):
        out, err = runPyExe(exepath, input="""import requests
print(requests.get.__doc__)
""")
        assert 'Sends a GET request' in out


def testFromStdin(exepath):
    noblanks = """# No blank lines
def add(a, b):
  return a + b
print(sum([add(x, x + 1) for x in range(10)]))
"""
    blanks = """# Blank lines

def add(a, b):
  return a + b

print(sum([add(x, x + 1) for x in range(10)]))
"""
    out, err = runPyExe(exepath, input=noblanks)
    assert '100' in out
    # With -i, we need to have blank lines, since the processing is done
    # differently.
    out, err = runPyExe(exepath, ['-i'], input=noblanks)
    assert 'SyntaxError: invalid syntax' in err
    out, err = runPyExe(exepath, ['-i'], input=blanks)
    assert '100' in out
    assert not err.startswith('>>>')
    # Running a command first shouldn't affect the input processing.
    out, err = runPyExe(exepath, ['-i', '-c', 'import sys'], input=noblanks)
    assert 'SyntaxError: invalid syntax' in err
    out, err = runPyExe(exepath, ['-i', '-c', 'import sys'], input=blanks)
    assert '100' in out
    assert err.startswith('>>>')
    # Using an environment variable should check for a tty
    out, err = runPyExe(exepath, input=noblanks, env={'PYTHONINSPECT': 'true'})
    assert '100' in out


@contextlib.contextmanager
def pipInstalled(exepath, package, assertText):
    """
    Install a package with pip into the current directory, as the stand-alone
    usage describes, and remove what it installed on exit, so that the
    packages' own test modules do not get collected by later test runs.

    Enter: exepath: the fixture parameter.
           package: the package name to install.
           assertText: text asserted to be in the pip output.
    """
    before = set(os.listdir('.'))
    out, err = runPyExe(exepath, [
        '-m', 'pip', 'install', '--no-cache-dir', '--target', '.',
        '--upgrade', package])
    assert assertText in out
    try:
        yield out, err
    finally:
        # Ignore removal errors, in case files are still locked.
        for entry in set(os.listdir('.')) - before:
            try:
                if os.path.isdir(entry):
                    shutil.rmtree(entry, ignore_errors=True)
                else:
                    os.unlink(entry)
            except OSError:
                pass


def testHyphen(exepath):
    out, err = runPyExe(exepath, ['-', 'param1', "'param2'"], input="""import sys
print(sys.argv)
""")
    assert """['-', 'param1', "'param2'"]""" in out


def testZipApp(exepath):
    out, err = runPyExe(exepath, ['..\\sample_zipapp.pyz'])
    assert '15' in out


def testSkipHeader(exepath):
    out, err = runPyExe(exepath, ['sample_skip_header.py'])
    assert 'SyntaxError: invalid syntax' in err
    out, err = runPyExe(exepath, ['-x', 'sample_skip_header.py'])
    assert 'skipped header' in out
    out, err = runPyExe(exepath, ['sample_no_header.py'])
    assert 'no header' in out


def testUnbuffered(exepath):
    delayed = """import time;print('Line 1');time.sleep(1);print('Line 2')"""
    out, err = runPyExeLines(exepath, ['-c', delayed])
    assert out[1][0] - out[0][0] < 0.5
    out, err = runPyExeLines(exepath, ['-u', '-c', delayed])
    assert out[1][0] - out[0][0] > 0.5
    out, err = runPyExeLines(exepath, ['-c', delayed], env={'PYTHONUNBUFFERED': 'true'})
    assert out[1][0] - out[0][0] > 0.5
    out, err = runPyExeLines(exepath, ['-E', '-c', delayed], env={'PYTHONUNBUFFERED': 'true'})
    assert out[1][0] - out[0][0] < 0.5


def testPopen2(exepath):
    # Issue #25: the Python 3.5 and 3.6 executables failed when driven
    # through pipes as with popen2, raising a ValueError from os.fdopen in
    # the handling of the standard streams.  The interactive interpreter
    # should work over open pipes, with and without unbuffered mode.
    commands = ['print(40 + 2)\n', 'exit()\n']
    for options in (['-i'], ['-u', '-i']):
        returncode, out, err = runPyExePopen2(exepath, options, commands)
        assert returncode == 0
        assert '42' in out
        assert 'ValueError' not in out + err


@pytest.mark.skipif(sys.platform != 'win32', reason='Requires Windows handle semantics.')
def testUnbufferedMissingStdHandles(exepath):
    # Unbuffered mode reopens the standard streams from their file
    # descriptors, which must keep working when the parent process does not
    # supply all of the standard handles (the historical popen2 use case).
    code = 'import sys;sys.stdout.write("out\\n");sys.stderr.write("err\\n")'
    returncode, out, err = runPyExeWithoutStdHandles(
        exepath, ['-u', '-c', code], ['stdout'])
    assert returncode == 0
    assert b'out' in out
    returncode, out, err = runPyExeWithoutStdHandles(
        exepath, ['-u', '-c', code], ['stderr'])
    assert returncode == 0
    assert b'err' in err
    # The same runs behave the same without -u.
    returncode, out, err = runPyExeWithoutStdHandles(
        exepath, ['-c', code], ['stdout'])
    assert returncode == 0
    assert b'out' in out
    returncode, out, err = runPyExeWithoutStdHandles(
        exepath, ['-c', code], ['stderr'])
    assert returncode == 0
    assert b'err' in err


def testPythonPath(exepath):
    out, err = runPyExe(exepath, ['sample_print_path.py'],
                        env={'PYTHONPATH': 'C:\\Temp;C:\\nowhere'})
    assert "'C:\\\\Temp'" in out
    out, err = runPyExe(exepath, ['-E', 'sample_print_path.py'],
                        env={'PYTHONPATH': 'C:\\Temp;C:\\nowhere'})
    assert "'C:\\\\Temp'" not in out


def testIsolateFlag(exepath, pyversion):
    if pyversion >= (3, ):
        local = os.path.split(os.path.abspath('sample_print_path.py'))[0]
        localrepr = repr(local)
        out, err = runPyExe(exepath, ['sample_print_path.py'],
                            env={'PYTHONPATH': 'C:\\Temp'})
        assert localrepr in out
        assert "'C:\\\\Temp'" in out
        out, err = runPyExe(exepath, ['-I', 'sample_print_path.py'],
                            env={'PYTHONPATH': 'C:\\Temp'})
        assert localrepr not in out
        assert "'C:\\\\Temp'" not in out


def testQuietFlag(exepath, pyversion):
    if pyversion >= (3, ):
        out, err = runPyExe(exepath, ['-i'], input='print("here")')
        assert not err.startswith('>>>')
        out, err = runPyExe(exepath, ['-q', '-i'], input='print("here")')
        assert err.startswith('>>>')


def testStartup(exepath, pyversion):
    out, err = runPyExe(exepath, ['-i'], input='print("here")')
    assert '>>>' in err
    assert '-->' not in err
    out, err = runPyExe(exepath, ['-i'], input='print("here")',
                        env={'PYTHONSTARTUP': 'sample_startup.py'})
    assert '>>>' not in err
    assert '-->' in err
    out, err = runPyExe(exepath, ['-i', '-E'], input='print("here")',
                        env={'PYTHONSTARTUP': 'sample_startup.py'})
    assert '>>>' in err
    assert '-->' not in err


def testIOEncoding(exepath):
    command = 'import sys; print(sys.stdout.encoding, sys.stdout.errors)'
    out, err = runPyExe(exepath, ['-c', command],
                        env={'PYTHONIOENCODING': 'latin-1'})
    assert 'iso8859-1' in out or 'latin-1' in out
    out, err = runPyExe(exepath, ['-c', command],
                        env={'PYTHONIOENCODING': 'latin-1:replace'})
    assert 'iso8859-1 replace' in out or 'latin-1 replace' in out
    out, err = runPyExe(exepath, ['-c', command],
                        env={'PYTHONIOENCODING': ':backslashreplace'})
    assert 'backslashreplace' in out
    # The -E and -I flags ignore the environment variable.
    out, err = runPyExe(exepath, ['-E', '-c', command],
                        env={'PYTHONIOENCODING': 'latin-1'})
    assert 'iso8859-1' not in out
    assert 'latin-1' not in out
    out, err = runPyExe(exepath, ['-I', '-c', command],
                        env={'PYTHONIOENCODING': 'latin-1'})
    assert 'iso8859-1' not in out
    assert 'latin-1' not in out
    # The encoding and error handler apply when writing text that cannot be
    # encoded with the default encoding.
    out, err = runPyExe(exepath, ['-c', "import sys; sys.stdout.write('caf\\u20ac\\n')"],
                        env={'PYTHONIOENCODING': 'latin-1:backslashreplace'})
    assert 'caf\\u20ac' in out
    # stdin and stderr get the same encoding.
    out, err = runPyExe(exepath, ['-c', 'import sys; print(sys.stdin.encoding)'],
                        env={'PYTHONIOENCODING': 'latin-1'})
    assert 'iso8859-1' in out or 'latin-1' in out
    out, err = runPyExe(exepath, ['-c', 'import sys; print(sys.stderr.encoding)'],
                        env={'PYTHONIOENCODING': 'latin-1'})
    assert 'iso8859-1' in out or 'latin-1' in out
    # An unknown encoding is an error, like in the python executable.
    out, err = runPyExe(exepath, ['-c', 'import sys'],
                        env={'PYTHONIOENCODING': 'bogus-encoding'})
    assert 'unknown encoding' in err


def testRunFileGlobals(exepath):
    out, err = runPyExe(exepath, ['sample_print_globals.py'])
    assert 'sys' not in out
    assert 'RunFile' not in out


def testCtypesAfterGlobalsAreCleared(exepath):
    # pyexe clears the global namespace before running a script or a command.
    # PyInstaller patches ctypes to look for libraries in sys._MEIPASS, and
    # historically those patches referenced a _frozen_name variable that was
    # bound in the main script's globals, so using ctypes after the globals
    # were cleared raised NameError (see pull request 47).  PyInstaller now
    # installs its ctypes patches from a module, so the patched loaders keep
    # working.  This test fails with a NameError if that regresses.
    code = """import ctypes
try:
    ctypes.CDLL('definitely_not_a_real_dll_xyz')
except NameError as err:
    print('NameError: %s' % (err))
except OSError as err:
    print('OSError')
"""
    path = 'sample_ctypes_frozen_name.py'
    try:
        open(path, 'w').write(code)
        out, err = runPyExe(exepath, [path])
        assert 'OSError' in out
        assert 'NameError' not in out
        assert 'NameError' not in err
    finally:
        os.unlink(path)
    out, err = runPyExe(exepath, input=code)
    assert 'OSError' in out
    assert 'NameError' not in out
    assert 'NameError' not in err
    # Command line arguments cannot contain newlines on Windows, so a one
    # line command is used for the '-c' path, where the error is reported on
    # stderr rather than caught.  The unfrozen python raises
    # FileNotFoundError, while the frozen executable raises OSError with a
    # message from PyInstaller.
    out, err = runPyExe(exepath, [
        '-c', "import ctypes; ctypes.CDLL('definitely_not_a_real_dll_xyz')"])
    assert 'OSError' in err or 'FileNotFoundError' in err
    assert 'NameError' not in out
    assert 'NameError' not in err


def testByteCodeFlag(exepath):
    clearPyc('sample_print_path.py')
    out, err = runPyExe(exepath, ['-i'], input='import sample_print_path.py')
    assert clearPyc('sample_print_path.py') == 1
    out, err = runPyExe(exepath, ['-B', '-i'], input='import sample_print_path.py')
    assert clearPyc('sample_print_path.py') == 0
    out, err = runPyExe(exepath, ['-i'], input='import sample_print_path.py',
                        env={'PYTHONDONTWRITEBYTECODE': 'true'})
    assert clearPyc('sample_print_path.py') == 0
    out, err = runPyExe(exepath, ['-E', '-i'], input='import sample_print_path.py',
                        env={'PYTHONDONTWRITEBYTECODE': 'true'})
    assert clearPyc('sample_print_path.py') == 1


def testOptimizeFlag(exepath):
    clearPyc('sample_optimize.py')
    out, err = runPyExe(exepath, [
        '-c', ('import sample_optimize;'
               'print(sample_optimize.test_optimize());'
               'print(sample_optimize.test_optimize.__doc__)')])
    assert 'AssertionError' in err
    clearPyc('sample_optimize.py')
    out, err = runPyExe(exepath, [
        '-O', '-c', ('import sample_optimize;'
                     'print(sample_optimize.test_optimize());'
                     'print(sample_optimize.test_optimize.__doc__)')])
    assert 'True' in out
    assert 'AssertionError' not in err
    assert 'This function' in out
    clearPyc('sample_optimize.py')
    out, err = runPyExe(exepath, [
        '-O', '-O', '-c', ('import sample_optimize;'
                           'print(sample_optimize.test_optimize());'
                           'print(sample_optimize.test_optimize.__doc__)')])
    assert 'True' in out
    assert 'AssertionError' not in err
    assert 'This function' not in out
    clearPyc('sample_optimize.py')
    out, err = runPyExe(exepath, [
        '-c', ('import sample_optimize;'
               'print(sample_optimize.test_optimize());'
               'print(sample_optimize.test_optimize.__doc__)')],
        env={'PYTHONOPTIMIZE': '2'})
    assert 'True' in out
    assert 'AssertionError' not in err
    assert 'This function' not in out
    clearPyc('sample_optimize.py')
    out, err = runPyExe(exepath, [
        '-c', ('import sample_optimize;'
               'print(sample_optimize.test_optimize());'
               'print(sample_optimize.test_optimize.__doc__)')],
        env={'PYTHONOPTIMIZE': '-1'})
    assert 'True' in out
    assert 'AssertionError' not in err
    assert 'This function' in out
    clearPyc('sample_optimize.py')
    out, err = runPyExe(exepath, [
        '-E', '-c', ('import sample_optimize;'
                     'print(sample_optimize.test_optimize());'
                     'print(sample_optimize.test_optimize.__doc__)')],
        env={'PYTHONOPTIMIZE': '2'})
    assert 'AssertionError' in err


def testVerboseFlag(exepath, pyversion):
    if pyversion >= (3, 11):
        # The verbosity flag cannot be applied after the interpreter starts
        # in Python 3.11+, since sys.flags is read-only and the legacy
        # Py_VerboseFlag global is no longer consulted.
        import pytest
        pytest.skip('The -v flag cannot be applied after start on Python 3.11+')
    out, err = runPyExe(exepath, ['-c', 'import bisect'])
    assert 'bisect' not in err
    assert '# cleanup' not in err
    out, err = runPyExe(exepath, ['-v', '-c', 'import bisect'])
    assert 'bisect' in err
    assert '# cleanup' in err
    assert 'clear[2]' not in err
    out, err = runPyExe(exepath, ['-v', '-v', '-c', 'import bisect'])
    assert 'bisect' in err
    assert '# cleanup' in err
    assert 'clear[2]' in err
    out, err = runPyExe(exepath, ['-c', 'import bisect'],
                        env={'PYTHONVERBOSE': '2'})
    assert 'bisect' in err
    assert '# cleanup' in err
    assert 'clear[2]' in err
    out, err = runPyExe(exepath, ['-E', '-c', 'import bisect'],
                        env={'PYTHONVERBOSE': '2'})
    assert 'bisect' not in err
    assert '# cleanup' not in err


def testBytesWarningFlag(exepath, pyversion):
    if pyversion >= (3, 11):
        # The bytes warning flag cannot be applied after the interpreter
        # starts in Python 3.11+, since the legacy Py_BytesWarningFlag global
        # is no longer consulted by the interpreter internals.
        import pytest
        pytest.skip('The -b flag cannot be applied after start on Python 3.11+')
    if pyversion >= (3, ):
        out, err = runPyExe(exepath, ['-c', 'print(str(b"abc"))'])
        assert 'abc' in out
        assert 'BytesWarning' not in err
        out, err = runPyExe(exepath, ['-b', '-c', 'print(str(b"abc"))'])
        assert 'abc' in out
        assert 'BytesWarning' in err
        out, err = runPyExe(exepath, ['-b', '-b', '-c', 'print(str(b"abc"))'])
        assert 'abc' not in out
        assert 'BytesWarning' in err


def testDivisionFlag(exepath, pyversion):
    if pyversion < (3, ):
        out, err = runPyExe(exepath, ['-c', 'print("%r" % [11/4, 7.0/4])'])
        assert '[2, 1.75]' in out
        assert 'division' not in err
        out, err = runPyExe(exepath, ['-Qold', '-c', 'print("%r" % [11/4, 7.0/4])'])
        assert '[2, 1.75]' in out
        assert 'division' not in err
        out, err = runPyExe(exepath, ['-Qwarn', '-c', 'print("%r" % [11/4, 7.0/4])'])
        assert '[2, 1.75]' in out
        assert 'classic int division' in err
        assert 'classic float division' not in err
        out, err = runPyExe(exepath, ['-Qwarnall', '-c', 'print("%r" % [11/4, 7.0/4])'])
        assert '[2, 1.75]' in out
        assert 'classic int division' in err
        assert 'classic float division' in err
        out, err = runPyExe(exepath, ['-Qnew', '-c', 'print("%r" % [11/4, 7.0/4])'])
        assert '[2.75, 1.75]' in out
        assert 'division' not in err


def testTabcheckFlag(exepath, pyversion):
    withtabs = """def add(a, b, c):
        sum = a + b
\treturn sum + c
print(add(1, 2, 3))"""
    if pyversion < (3, ):
        out, err = runPyExe(exepath, input=withtabs)
        assert '6' in out
        assert 'inconsistent use of tabs' not in err
        out, err = runPyExe(exepath, ['-t'], input=withtabs)
        assert '6' in out
        assert 'inconsistent use of tabs' in err
        assert 'TabError' not in err
        out, err = runPyExe(exepath, ['-t', '-t'], input=withtabs)
        assert '6' not in out
        assert 'inconsistent use of tabs' in err
        assert 'TabError' in err


def testPy3Flag(exepath, pyversion):
    oldclassexc = """class old:
  pass
raise old()
"""
    if pyversion < (3, ):
        out, err = runPyExe(exepath, input=oldclassexc)
        assert '__main__.old:' in err
        assert 'BaseException' not in err
        out, err = runPyExe(exepath, ['-3'], input=oldclassexc)
        assert '__main__.old:' in err
        assert 'BaseException' in err


def testWarningsOption(exepath):
    zipwarn = """import io
import zipfile

buf = io.BytesIO()
with zipfile.ZipFile(buf, 'a') as z:
  z.writestr('name', 'data')
  z.writestr('name', 'data2')
"""
    out, err = runPyExe(exepath, input=zipwarn)
    assert "Duplicate name: 'name'" in err
    assert 'Traceback' not in err
    out, err = runPyExe(exepath, ['-Werror'], input=zipwarn)
    assert "Duplicate name: 'name'" in err
    assert 'Traceback' in err
    out, err = runPyExe(exepath, ['-W', 'error'], input=zipwarn)
    assert "Duplicate name: 'name'" in err
    assert 'Traceback' in err
    out, err = runPyExe(exepath, input=zipwarn, env={'PYTHONWARNINGS': 'error'})
    assert "Duplicate name: 'name'" in err
    assert 'Traceback' in err
    out, err = runPyExe(exepath, ['-E'], input=zipwarn, env={'PYTHONWARNINGS': 'error'})
    assert "Duplicate name: 'name'" in err
    assert 'Traceback' not in err


def testPythonCaseOK(exepath):
    # For these tests, we don't write bytecode files, as that can cache the
    # results.
    out, err = runPyExe(exepath, ['-B', '-c', 'import sample_case'])
    assert 'mixed CASE' not in out
    assert 'No module named' in err
    out, err = runPyExe(exepath, ['-B', '-c', 'import sample_case'],
                        env={'PYTHONCASEOK': 'true'})
    assert 'mixed CASE' in out
    assert 'No module named' not in err
    # Python 3.9+ ignores PYTHONCASEOK when -E or -I is given, and the
    # stand-alone executable matches that behavior.
    out, err = runPyExe(exepath, ['-B', '-E', '-c', 'import sample_case'],
                        env={'PYTHONCASEOK': 'true'})
    assert 'mixed CASE' not in out
    assert 'No module named' in err
    out, err = runPyExe(exepath, ['-B', '-I', '-c', 'import sample_case'],
                        env={'PYTHONCASEOK': 'true'})
    assert 'mixed CASE' not in out
    assert 'No module named' in err


@pytest.mark.pyexe
def testBuildPathNotInTracebacks(exepath, haspsutil):
    if not haspsutil:
        import pytest
        pytest.skip('psutil is not bundled (free-threaded builds)')
    out, err = runPyExe(exepath, [
        '-c', """import psutil;psutil.net_connections('foo')"""])
    # With PyInstaller 6, module paths in tracebacks are shown relative to
    # the bundled package, such as psutil\_pswindows.py, rather than the
    # original site-packages paths.
    assert 'psutil' in err
    assert 'C:\\Python' not in err


def testImportFromExePath(exepath):
    # A virtual environment's python does not search the directory of the
    # executable for modules, so this test only applies to full python
    # installations and to the stand-alone executable.
    exedir = os.path.dirname(os.path.abspath(exepath))
    if (os.path.isfile(os.path.join(exedir, 'pyvenv.cfg')) or
            os.path.isfile(os.path.join(os.path.dirname(exedir), 'pyvenv.cfg'))):
        pytest.skip('The python is from a virtual environment')
    modpath = os.path.join(os.path.dirname(exepath), 'mod_exepath.py')
    try:
        open(modpath, 'w').write('foo = "bar"')
        out, err = runPyExe(exepath, ['-c', 'import mod_exepath;print(mod_exepath.foo)'])
        assert 'bar' in out
    finally:
        os.unlink(modpath)
    sitepath = os.path.join(os.path.dirname(exepath), 'Lib', 'site-packages')
    modpath = os.path.join(sitepath, 'mod_libsite.py')
    try:
        os.makedirs(sitepath)
    except Exception:
        pass
    try:
        open(modpath, 'w').write('foo = "baz"')
        out, err = runPyExe(exepath, ['-c', 'import mod_libsite;print(mod_libsite.foo)'])
        assert 'baz' in out
    finally:
        os.unlink(modpath)
        try:
            os.removedirs(sitepath)
        except Exception:
            pass


def testSubprocesNonPython(exepath):
    out, err = runPyExe(exepath, [
        '-c', 'import subprocess;subprocess.call(["nslookup.exe", "github.com"])'])
    assert 'Address' in out


def testThreadGlobals(exepath):
    out, err = runPyExe(exepath, ['sample_thread_globals.py'])
    assert 'Global Variable' in out


def testThreadGlobalsInput(exepath):
    code = """# Thread function with globals
import threading
import time

def threaded_func():
    time.sleep(1)
    print(globalVar)

globalVar = "Global Variable"
threading.Thread(target=threaded_func).start()
"""
    out, err = runPyExe(exepath, input=code)
    assert 'Global Variable' in out


def testSourceWithEncoding(exepath, pyversion):
    import codecs
    helloworld = '\u4f60\u597d\uff0c\u4e16\u754c'
    code = """import codecs
import sys

sys.stdout = codecs.getwriter("utf-8")(
    sys.stdout if sys.version_info[0] < 3 else sys.stdout.detach())
# %s
print(%r)\n""" % (helloworld, helloworld)
    for enc, header in (
            ('utf-8', b''),
            ('utf-8-bom', codecs.BOM_UTF8),
            ('cp950', b''),
            ('gbk', b''),
            # Note that python source code cannot be in utf-16 or utf-32
    ):
        path = 'sample_encoding_%s.py' % enc
        if enc.endswith('-bom'):
            enc = enc[:-4]
        data = header
        if not header and (enc != 'utf-8' or pyversion < (3, )):
            data += ('# encoding: %s\n' % enc.rstrip('ble')).encode(enc)
        data += code.encode(enc)
        open(path, 'wb').write(data)
        out, err = runPyExe(exepath, [path])
        assert helloworld in out
