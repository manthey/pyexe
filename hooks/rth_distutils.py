# Keep the stand-alone executable from importing setuptools at startup, and
# install the distutils shim that PyInstaller's automatic pyi_rth_setuptools
# runtime hook would otherwise install.
#
# The PyInstaller hook imports setuptools (which costs several hundred
# milliseconds at every startup) just to read setuptools.__version__ and
# install the distutils shim, which diverts `import distutils` to
# setuptools._distutils.  The bundled setuptools is always version 60 or
# newer, so the default value of SETUPTOOLS_USE_DISTUTILS is 'local', and
# the shim can be installed directly from the lightweight _distutils_hack
# module, without importing setuptools at all.
#
# To keep the PyInstaller hook from importing setuptools anyway, this module
# also installs a meta path finder that makes that import fail fast; the
# PyInstaller hook catches the failure and does nothing else, and the distutils
# shim was already installed by this module.  The blocker stays installed
# until pyexe.py (the entry script, which runs after all of the runtime
# hooks) removes it, so that user code can import setuptools normally; the
# blocker is passed to pyexe.py through the __main__ module's namespace,
# which the runtime hooks are exec'd in.  (The build-time test that imports
# all bundled modules fails loudly if any future runtime hook needs to
# import setuptools at startup.)
import os
import sys


def install_distutils_shim():
    """
    Install the distutils shim (the equivalent of setuptools'
    distutils-precedence.pth), which makes `import distutils` use
    setuptools._distutils, as modern setuptools does by default.  Returns
    True if the shim was installed.
    """
    # With setuptools < 60 the default would be 'stdlib' instead and the
    # shim must not be installed; the bundled setuptools is far newer, but
    # an explicit environment setting is honored all the same.
    if os.environ.get('SETUPTOOLS_USE_DISTUTILS', 'local') != 'local':
        return False
    try:
        import _distutils_hack
        _distutils_hack.add_shim()
    except Exception:
        return False
    return True


class SetuptoolsImportBlocker:
    """
    A meta path finder that makes the `import setuptools` in PyInstaller's
    automatic pyi_rth_setuptools runtime hook fail fast, so that setuptools
    is not loaded at startup; the hook catches the error and does nothing
    else, and the distutils shim was already installed by this module.  The
    blocker is removed by pyexe.py once all of the runtime hooks have run.
    """

    def find_spec(self, fullname, path=None, target=None):
        if fullname == 'setuptools':
            msg = ('setuptools is not imported during the startup of the '
                   'stand-alone executable; import it again if necessary')
            raise ImportError(msg)
        return


if 'setuptools' not in sys.modules and install_distutils_shim():
    _setuptools_import_blocker = SetuptoolsImportBlocker()
    sys.meta_path.insert(0, _setuptools_import_blocker)
