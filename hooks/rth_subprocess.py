import contextlib
import subprocess
import sys


class _pyexePopen(subprocess.Popen):
    if sys.version_info >= (3, ):
        def __init__(self, args, bufsize=-1, executable=None, stdin=None,
                     stdout=None, stderr=None, preexec_fn=None,
                     close_fds=getattr(subprocess, '_PLATFORM_DEFAULT_CLOSE_FDS', True),
                     shell=False, cwd=None, env=None, *arglist, **kwargs):
            with self._prepare_env(args, executable, env):
                result = super(_pyexePopen, self).__init__(
                    args, bufsize, executable, stdin, stdout, stderr,
                    preexec_fn, close_fds, shell, cwd, env, *arglist, **kwargs)
            return result
    else:
        def __init__(self, args, bufsize=0, executable=None, stdin=None,
                     stdout=None, stderr=None, preexec_fn=None,
                     close_fds=False, shell=False, cwd=None, env=None,
                     *arglist, **kwargs):
            with self._prepare_env(args, executable, env):
                result = super(_pyexePopen, self).__init__(
                    args, bufsize, executable, stdin, stdout, stderr,
                    preexec_fn, close_fds, shell, cwd, env, *arglist, **kwargs)
            return result

    @contextlib.contextmanager
    def _prepare_env(self, args, executable, env):
        import os
        import six
        import sys

        inparam = False
        inenv = False
        origname = None
        if (not isinstance(args, six.string_types) and len(args) >= 1 and
                getattr(sys, '_MEIPASS', None)):
            exename = args[0]
            exelower = exename.lower()
            if exelower.endswith('.exe'):
                exelower = exelower.rsplit('.', 1)[0]
            if (exename == sys.executable or exelower in (
                    'python', 'python%d' % sys.version_info[0],
                    'python%d%d' % (sys.version_info[0], sys.version_info[1]))):
                if env:
                    if '_MEIPASS2' not in env:
                        inparam = True
                        env['_MEIPASS2'] = sys._MEIPASS
                else:
                    inenv = os.getenv('_MEIPASS2', None)
                    os.putenv('_MEIPASS2', sys._MEIPASS)
                origname = exename
                args[0] = sys.executable
        yield
        if origname:
            args[0] = origname
        if inparam:
            del env['_MEIPASS2']
        if inenv is not False:
            if hasattr(os, 'unsetenv') and inenv is None:
                os.unsetenv('_MEIPASS2')
            else:
                os.putenv('_MEIPASS2', inenv or '')


subprocess.Popen = _pyexePopen
