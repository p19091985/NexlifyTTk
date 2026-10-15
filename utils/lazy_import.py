"""
Helpers for delaying heavyweight optional imports until first attribute access.
"""

from __future__ import annotations

from importlib import import_module


class LazyModule:
    """Proxy object that imports a module the first time it is used."""

    __slots__ = ("_module_name", "_module", "__dict__")

    def __init__(self, module_name: str):
        self._module_name = module_name
        self._module = None

    def _load(self):
        module = self._module
        if module is None:
            module = import_module(self._module_name)
            self._module = module
        return module

    def __getattr__(self, name):
        return getattr(self._load(), name)
