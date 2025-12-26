from functools import lru_cache

__all__ = ["get_public_methods", "freeze_dataclass"]


@lru_cache(maxsize=4)
def get_public_methods(cls) -> list[str]:
    return [e for e in dir(cls) if not e.startswith("_") and callable(getattr(cls, e))]


def freeze_dataclass(cls):
    """
    Modify the class in-place to behave like a frozen dataclass.
    Reversible via _unfreeze_dataclass().
    """
    if hasattr(cls, "__frozen_original__"):
        return cls  # idempotent

    cls.__frozen_original__ = {
        "__setattr__": getattr(cls, "__setattr__", None),
        "__delattr__": getattr(cls, "__delattr__", None),
    }

    def frozen_setattr(self, name, value):
        raise TypeError(f"{cls.__name__} is frozen; cannot assign to field '{name}'")

    def frozen_delattr(self, name):
        raise TypeError(f"{cls.__name__} is frozen; cannot delete field '{name}'")

    cls.__setattr__ = frozen_setattr
    cls.__delattr__ = frozen_delattr
    return cls


def unfreeze_dataclass(cls):
    orig = getattr(cls, "__frozen_original__", None)
    if not orig:
        return cls

    if orig["__setattr__"] is not None:
        cls.__setattr__ = orig["__setattr__"]
    else:
        del cls.__setattr__

    if orig["__delattr__"] is not None:
        cls.__delattr__ = orig["__delattr__"]
    else:
        del cls.__delattr__

    del cls.__frozen_original__
    return cls
