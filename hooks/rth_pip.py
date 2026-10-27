# Register a distlib resource finder for PyInstaller's frozen importers, so
# that pip's vendored distlib can locate resources when running from the
# stand-alone executable.  distlib's finder function looks up the loader type
# of the imported package in distlib.resources._finder_registry, and the
# PyInstaller frozen importers are not in its default registry, so pip's
# ScriptMaker (used when installing wheels) fails without this registration.
#
# Importing pip's vendored distlib here would cost several hundred
# milliseconds of startup for every run of the stand-alone executable, since
# distlib.util pulls in logging, ssl, hashlib, socket, and other substantial
# modules, and this executable is usually not used to run pip at all.
# Therefore, the registration is deferred: a meta path finder observes the
# first import of pip's vendored distlib resources module and wraps its
# loader, so the registration happens right after that module is executed,
# before any distlib code can consult the registry (the only consumer,
# distlib.resources.finder, is called after the import completes).
#
# All of the deferred code binds its dependencies as instance attributes or
# default arguments: the runtime hooks are exec'd in the __main__ module's
# namespace, whose globals pyexe.py clears when running a script file, so
# module-level names would be lost by the time the deferred code runs.
import sys


def register_distlib_finder(_sys, _hook_loader):
    """
    Add the PyInstaller frozen importers to distlib's resource finder
    registry.  Returns True if the registration succeeded.
    """
    try:
        # This import is also what makes the build collect pip's vendored
        # distlib; by the time this runs, the module has just been executed,
        # so this only fetches it from sys.modules.
        import pip._vendor.distlib.resources as resources
    except ImportError:
        return False
    try:
        _frozen_module = _sys.modules.get('pyimod02_importers')
        if _frozen_module is None:
            try:
                from PyInstaller.loader import \
                    pyimod02_importers as _frozen_module
            except ImportError:
                _frozen_module = None
        if _frozen_module is not None:
            for _cls_name in ('PyiFrozenLoader', 'PyiFrozenEntryPointLoader'):
                _cls = getattr(_frozen_module, _cls_name, None)
                if _cls is not None:
                    resources._finder_registry[_cls] = resources.ResourceFinder
        if _hook_loader is not None:
            resources._finder_registry[type(_hook_loader)] = \
                resources.ResourceFinder
    except Exception:
        return False
    return True


class RegistrationLoader:
    """
    Delegate everything to the real loader, and perform the distlib
    registration right after the target module is executed.
    """

    def __init__(self, loader, register, sysmod, hook_loader):
        self._loader = loader
        self._register = register
        self._sys = sysmod
        self._hook_loader = hook_loader

    def __getattr__(self, name):
        return getattr(self._loader, name)

    def create_module(self, spec):
        return self._loader.create_module(spec)

    def exec_module(self, module):
        self._loader.exec_module(module)
        try:
            self._register(self._sys, self._hook_loader)
        except Exception:
            pass


class DeferredDistlibRegistration:
    """
    A meta path finder that wraps the loader of pip's vendored distlib
    resources module so that the registration happens after the module is
    executed.  It never resolves modules itself and removes itself from the
    meta path after the first trigger.
    """

    target = 'pip._vendor.distlib.resources'

    def __init__(self):
        self.sysmod = sys
        self.hook_loader = __loader__

    def find_spec(self, fullname, path=None, target=None):
        if fullname != self.target:
            return None
        try:
            self.sysmod.meta_path.remove(self)
        except ValueError:
            pass
        # The real finder for the target module is PyInstaller's frozen
        # importer, which is also on the meta path; find the spec with the
        # remaining finders and wrap its loader, so that the registration
        # happens after the module is executed.
        for finder in self.sysmod.meta_path:
            if finder is self:
                continue
            find_spec = getattr(finder, 'find_spec', None)
            if find_spec is None:
                continue
            try:
                spec = find_spec(fullname, path, target)
            except Exception:
                continue
            if spec is not None and spec.loader is not None:
                spec.loader = RegistrationLoader(
                    spec.loader, register_distlib_finder,
                    self.sysmod, self.hook_loader)
                return spec
        return None


# The finder must be at the front of the meta path: PyInstaller's frozen
# importer is also on the meta path and would otherwise resolve the target
# module (and everything else in the PYZ archive) before this finder is
# consulted.
sys.meta_path.insert(0, DeferredDistlibRegistration())
