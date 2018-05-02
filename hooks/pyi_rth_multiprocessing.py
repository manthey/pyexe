# This replaces PyInstaller\loader\rthooks\pyi_rth_multiprocessing.py
# Although pyexe.exe is frozen, we need to act like it is not frozen.  We still
# need PyInstaller's version of _Popen to use the same environment in the
# forked processes as the main process.


# Module multiprocessing is organized differently in Python 3.4+
try:
    import multiprocessing.popen_spawn_win32 as forking
    import multiprocessing.spawn

    multiprocessing.spawn.WINEXE = False
    multiprocessing.freeze_support = multiprocessing.spawn.freeze_support
except ImportError:
    import multiprocessing.forking as forking


class _Popen(forking.Popen):
    def __init__(self, *args, **kw):
        import os
        import sys

        oldValue = os.getenv('_MEIPASS2')
        os.putenv('_MEIPASS2', sys._MEIPASS)
        try:
            super(_Popen, self).__init__(*args, **kw)
        finally:
            if hasattr(os, 'unsetenv') and oldValue is None:
                os.unsetenv('_MEIPASS2')
            else:
                os.putenv('_MEIPASS2', oldValue or '')


forking.Popen = _Popen
forking.WINEXE = False
