import os
import pytest
import subprocess


@pytest.fixture
def exepath(request):
    return request.config.getoption("--exe")


def runPyExe(exepath, options=[], input='', env={}):
    """
    Enter: exepath: the fixture parameter.
           options: command line options to pass to the executable.
           input: data to pass via stdin.
           env: additional environment parameters.
    """
    cmd = [exepath] + options
    cmdenv = os.environ.copy()
    cmdenv.update(env)
    proc = subprocess.Popen(
        cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, env=cmdenv)
    out, err = proc.communicate(input)
    return out, err


def testVersion(exepath):
    out, err = runPyExe(exepath, ['--version'])
    assert out.startswith('Stand-Alone Python Interpreter')
    out, err = runPyExe(exepath, ['-V'])
    assert out.startswith('Stand-Alone Python Interpreter')
    assert 'psutil' not in out
    out, err = runPyExe(exepath, ['-V', '-V'])
    assert 'psutil' in out and 'pywin32' in out
    out, err = runPyExe(exepath, ['-VV'])
    assert 'psutil' in out and 'pywin32' in out


def testDirectCommand(exepath):
    out, err = runPyExe(exepath, ['-c', 'print("This is a test")'])
    assert out.startswith('This is a test')


def testDirectCommandImport(exepath):
    out, err = runPyExe(exepath, [
        '-c', """import json;print(json.dumps({'test':'value'}))"""])
    assert out.startswith('{"test": "value"}')


def testImportPsutil(exepath):
    out, err = runPyExe(exepath, [
        '-c', """import psutil;print(repr(psutil.cpu_times()))"""])
    assert 'scputimes' in out
    out, err = runPyExe(exepath, [
        '-c', """import psutil;print(repr(psutil.net_connections()))"""])
    assert 'raddr' in out


def testImportSix(exepath):
    out, err = runPyExe(exepath, [
        '-c', """import six;print(six.callable(six.BytesIO))"""])
    assert 'True' in out


def testImportPywin32(exepath):
    out, err = runPyExe(exepath, input="""import win32con
import win32file
print('%r' % [
  win32file.GetFileAttributes('.'), win32con.FILE_ATTRIBUTE_DIRECTORY])
""")
    assert '16, 16' in out


def testSiteValues(exepath):
    for key in ('quit', 'exit', 'help', 'copyright', 'credits', 'license'):
        out, err = runPyExe(exepath, input="""try:
  print(%s)
except Exception:
  pass
""" % key)
        assert key in out.lower() or 'python.org' in out


def testMultiprocessing(exepath):
    out, err = runPyExe(exepath, ['sample_multiprocessing.py'])
    assert 'Difference: (0)' in out


def testPySerialFromPip(exepath):
    out, err = runPyExe(exepath, [
        '-m', 'pip', 'install', '--no-cache-dir', '--target', '.',
        '--upgrade', 'pyserial'])
    assert 'Successfully installed pyserial' in out
    out, err = runPyExe(exepath, input="""from six.moves import range
import serial
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
    out, err = runPyExe(exepath, [
        '-m', 'pip', 'install', '--no-cache-dir', '--target', '.',
        '--upgrade', 'sympy'])
    assert 'Successfully installed' in out and 'sympy' in out
    out, err = runPyExe(exepath, input="""import sympy
x = sympy.Symbol('x')
result = sympy.simplify(1/x + (x*sympy.sin(x) - 1)/x)
print(result)
""")
    assert 'sin(x)' in out


def testHelp(exepath):
    for opt in ('--help', '-h', '-?', '/?'):
        out, err = runPyExe(exepath, [opt])
        assert 'Stand-alone specific options' in out


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
    # assert 'SyntaxError: invalid syntax' in err
    out, err = runPyExe(exepath, ['-i'], input=blanks)
    # assert '100' in out
    # Running a command first shouldn't affect the input processing.
    out, err = runPyExe(exepath, ['-i', '-c', 'import sys'], input=noblanks)
    assert 'SyntaxError: invalid syntax' in err
    out, err = runPyExe(exepath, ['-i', '-c', 'import sys'], input=blanks)
    assert '100' in out
    # Using an environment variable should check for a tty
    out, err = runPyExe(exepath, input=noblanks, env={'PYTHONINSPECT': 'true'})
    assert '100' in out


def testHyphen(exepath):
    out, err = runPyExe(exepath, ['-', 'param1', '\'param2\''], input="""import sys
print(sys.argv)
""")
    assert """['-', 'param1', "'param2'"]""" in out


def testAllFlag(exepath):
    out, err = runPyExe(exepath, ['--all', '-c', 'import sys;print(sorted(sys.modules.keys()))'])
    assert 'psutil' in out and 'multiprocessing' in out


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


# Add tests for:
#  command line options:
#    -u / PYTHONUNBUFFERED
#    -S
#    -E
