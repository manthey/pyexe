# Register a distlib resource finder for PyInstaller's frozen importers, so
# that pip's vendored distlib can locate resources when running from the
# stand-alone executable.
try:
    from pip._vendor.distlib import resources
except ImportError:
    pass
else:
    try:
        import sys

        _frozen_module = sys.modules.get('pyimod02_importers')
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
        if __loader__ is not None:
            resources._finder_registry[type(__loader__)] = resources.ResourceFinder
        # Runtime hooks are exec'd in the __main__ module's namespace, so
        # these module-level temporaries would otherwise leak into the
        # globals of the main script (and from there into the curated global
        # environment that pyexe passes to user code).
        if _frozen_module is None:
            del _frozen_module
        else:
            del _cls_name, _cls, _frozen_module
    except Exception:
        pass
