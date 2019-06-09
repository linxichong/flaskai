import weakref

class CoreMixin:
    def __init__(self, core):
        if core:
            self.core = core
    @property
    def core(self):
        return getattr(self, '_core', lambda: None)
    @core.setter
    def core(self, v):
        self._core = weakref.proxy(v)