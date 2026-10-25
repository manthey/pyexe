# This replaces the multiprocessing handling in PyInstaller.  Although
# pyexe.exe is frozen, we need to act like it is not frozen, so that the
# spawned child processes get prepared in the same way as the main process.
import multiprocessing.popen_spawn_win32 as forking
import multiprocessing.spawn

multiprocessing.spawn.WINEXE = False
multiprocessing.freeze_support = multiprocessing.spawn.freeze_support

forking.WINEXE = False
