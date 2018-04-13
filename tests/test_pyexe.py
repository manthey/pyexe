import pytest
import subprocess


@pytest.fixture
def exepath(request):
    return request.config.getoption("--exe")


def runPyExe(exepath, options=[], input=''):
    cmd = [exepath] + options
    proc = subprocess.Popen(
        cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    out, err = proc.communicate(input)
    return out, err


def testVersion(exepath):
    out, err = runPyExe(exepath, ['--version'])
    assert out.startswith('Stand-Alone Python Interpreter')
    out, err = runPyExe(exepath, ['-V'])
    assert out.startswith('Stand-Alone Python Interpreter')


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


# Add tests for:
#  command line options:
#    -i / PYTHONINSPECT
#    -h / --help /?
#    -m
#    -u / PYTHONUNBUFFERED
#    -S
#  multiprocessing
#  with source file
#    -x
#  stdin
#  pip install serial and then use it
