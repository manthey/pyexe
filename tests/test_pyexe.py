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


def testDirectCommand(exepath):
    out, err = runPyExe(exepath, ['-c', 'print("This is a test")'])
    assert out.startswith('This is a test')


def testDirectCommandImport(exepath):
    out, err = runPyExe(exepath, [
        '-c', """import json;print(json.dumps({'test':'value'}))"""])
    assert out.startswith('{"test": "value"}')


def testVersion(exepath):
    out, err = runPyExe(exepath, ['--version'])
    assert out.startswith('Stand-Alone Python Interpreter')
    out, err = runPyExe(exepath, ['-V'])
    assert out.startswith('Stand-Alone Python Interpreter')


# Add tests for:
#  importing psutil, six, pywin32
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
