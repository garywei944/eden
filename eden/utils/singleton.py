"""Testable Singleton class with Dependency Injection enforcement.

Doc: https://bytedance.us.larkoffice.com/docx/I9EsdRJM3ou2JaxVv1Ku63vSs9e

### Reference
Check out Google's 2008 Talk and Blog on "Global State and Singletons".
- https://bilibili.com/video/BV1mt4y12799/
- https://youtu.be/-FRm3VPhseI?si=S4q1MNzAejAf1_AZ
- https://testing.googleblog.com/2008/08/root-cause-of-singletons.html
"""

from __future__ import annotations

import enum
import logging
import os
import sys
import threading
from abc import ABC, ABCMeta
from concurrent import futures as ct
from dataclasses import dataclass, field
from typing import Self, cast, final

__all__ = ["Singleton", "SingletonMeta", "reset_singleton"]

logger = logging.getLogger(__name__)

_TLS = threading.local()


# Note that type[C] is covariant in PEP 585, Python 3.9+
# which means we are returning a list of subclasses of Singleton.
# https://docs.python.org/3/library/typing.html#the-type-of-class-objects
def _get_tls_working_classes() -> list[type[Singleton]]:
    """Per-thread local variable to store the bottom-up order of class inheritance"""
    if not hasattr(_TLS, "working_classes"):
        _TLS.working_classes = []
    return _TLS.working_classes


class SingletonFactoryState(enum.Enum):
    IDLE = enum.auto()
    WORKING = enum.auto()
    SUCCESS = enum.auto()
    FAILED = enum.auto()


@dataclass
class SingletonMetadata:
    instance: ct.Future = field(default_factory=ct.Future)
    state: SingletonFactoryState = SingletonFactoryState.IDLE
    singleton_lock: threading.Lock = field(default_factory=threading.Lock)
    owned_singletons: set[type[Singleton]] = field(default_factory=set)


def _get_meta_dict(
    cls: type[Singleton], init: bool = False
) -> dict[type[Singleton], SingletonMetadata]:
    """Get or create the singleton metadata dict under the module of cls."""
    module = sys.modules[cls.__module__]
    if not hasattr(module, "__singleton_meta_dict__"):
        if init:
            setattr(module, "__singleton_meta_dict__", dict())
        else:
            raise RuntimeError(
                f"SingletonMetadata dict not found under {module}. "
                "There is something wrong with module import."
            )

    return module.__singleton_meta_dict__


def _get_metadata(cls: type[Singleton]) -> SingletonMetadata:
    """Get the SingletonMetadata for the given singleton class."""
    meta_dict = _get_meta_dict(cls)
    if cls not in meta_dict:
        raise RuntimeError(f"SingletonMetadata for {cls.__name__} not found")
    return meta_dict[cls]


class SingletonMeta(ABCMeta):
    def __init__(cls, name, bases, namespace, /, **kwargs):
        super().__init__(name, bases, namespace, **kwargs)

        # ! This is race-condition-free since all creation happens at module load time, and
        # ! module load is guaranteed to be single-threaded by Python interpreter.

        # During import time, initialize the singleton metadata for each singleton class.
        _cls = cast(type["Singleton"], cls)
        _get_meta_dict(_cls, init=True)[_cls] = SingletonMetadata()

    def __call__(cls, *args, **kwargs):
        """Construct the singleton instance."""
        _cls = cast(type["Singleton"], cls)

        working_classes = _get_tls_working_classes()
        if _cls in working_classes:
            raise SelfRecursiveConstructionError("Circular construction detected")

        metadata = _get_metadata(_cls)

        # This is the construction
        is_root_owner = not working_classes
        working_classes.append(_cls)
        try:
            # Check if a non-leaf class is initialized
            with metadata.singleton_lock:
                if metadata.state in [
                    SingletonFactoryState.WORKING,
                    SingletonFactoryState.SUCCESS,
                ]:
                    raise ManyConstructionError(f"{_cls.__name__} already initialized")

                if metadata.state == SingletonFactoryState.FAILED:
                    metadata.instance = ct.Future()
                metadata.state = SingletonFactoryState.WORKING
            if not is_root_owner:
                # Track ownership for classes, so that we can clean up properly in tests
                _get_metadata(working_classes[-2]).owned_singletons.add(_cls)

            # Release the lock and then do block initialization
            try:
                # cls.__init__() is called inside super().__call__()
                # so this line of code is instantiate and initialize the singleton instance.
                instance = super().__call__(*args, **kwargs)
            except BaseException as e:
                with metadata.singleton_lock:
                    metadata.state = SingletonFactoryState.FAILED
                    metadata.instance.set_exception(e)

                    if metadata.owned_singletons:
                        # ! It's not safe to automatically clean up owned singletons here,
                        # ! because other threads may be using them.
                        logger.critical(
                            "[Singleton] Critical: Singleton %s failed to initialize, "
                            "but it owns other singletons: [%s]. "
                            "These singletons may be leaked and need manual cleanup.",
                            cls.__name__,
                            ", ".join(s.__name__ for s in metadata.owned_singletons),
                        )
                raise e
            else:
                with metadata.singleton_lock:
                    metadata.state = SingletonFactoryState.SUCCESS
                    metadata.instance.set_result(instance)
                return instance
        finally:
            working_classes.pop()


class Singleton(ABC, metaclass=SingletonMeta):
    """Testable Thread-safe Singleton class

    https://bytedance.us.larkoffice.com/docx/I9EsdRJM3ou2JaxVv1Ku63vSs9e

    - Supports subclassing, @dataclass, and type hinting.
        - ***Note that since Singleton is thread-safe and supports subclassing, all sub-classes \
            of Singleton must also be thread safe.***
        - Sub-classing are considered different instances.
    - Enforce Once-and-Only-Once and Dependency Injection principles
        - Necessary for correct parallel testing which prevents mutable global states.

    Usage:
    ```python
    @dataclass
    class MySingleton(Singleton):
        attribute: int
        def __post_init__(self):
            self.attribute = 42

    # To initialize a singleton instance
    singleton_instance = MySingleton(attribute=42)
    # Then to use it by getting the reference of the instance
    singleton_instance = MySingleton.instance()
    # .instance() will blocks until the instance is ready, optionally give it a timeout
    singleton_instance = MySingleton.instance(timeout=5.0)
    # The second and following construction raises RuntimeError
    MySingleton(); MySingleton()  # raises RuntimeError

    # If Singleton A depends Singleton B for initialization, it must be stated explicitly.
    class MyDependentSingleton(Singleton):
        def __init__(self, dependency: MySingleton):
            # self.dependency = MySingleton.instance() raises RuntimeError.
            self.dependency = dependency

    # To correctly inherit from Singleton without MRO(Method Resolution Order) error,
    # always inherit Singleton last.
    class MySubSingleton(SomeBaseSingletonClass, Singleton):
        pass

    # Specifies `Singleton` by inheriting another Singleton class is optional
    # The following class is equivalent to the above
    class MySubSingleton(SomeBaseSingletonClass)
        pass
    ```

    ### For Tests
    - Mock the singleton instance per-test as needed.
    - ***Please don't hack/workaround with the CI environment***
        - e.g. `obj = MySingleton.instance() if not ci_env else WeirdClass()`.
        - Doing so makes the test codes meaningless and trivial.

    ### Global Lock order
    - In order to guarantee deadlock-free while inheritance, all singleton classes must
    acquire locks in the same partial order(topological order).
    - We agree that all locks are acquired from a top-down order and released reversely.
        - e.g. in class A, lock are acquire la1 -> la2
        - class B inherits from class A, and locks are acquired lb2 -> lb1
        - then in any method of class B, all locks must be acquired in the order la1 -> la2 -> lb2
        -> lb1
    - All locks should be Reentrant Locks (RLocks), except for the root singleton class.


    ### Reference
    Check out Google's 2008 Talk and Blog on "Global State and Singletons".
    - https://bilibili.com/video/BV1mt4y12799/
    - https://youtu.be/-FRm3VPhseI?si=S4q1MNzAejAf1_AZ
    - https://testing.googleblog.com/2008/08/root-cause-of-singletons.html
    """

    @classmethod
    @final
    def instance(cls, timeout: float | None = None) -> Self:
        """Get the singleton instance, blocking until it's ready.

        Args:
            timeout (float | None): Maximum time to wait for the instance to be ready.
                If None, wait indefinitely. Default is None.
        Raises:
            concurrent.ct.TimeoutError: If the instance is not ready within the timeout.
            DependencyInjectionViolationError: If called within the construction of another \
                singleton.
            SelfRecursiveReferenceError: If called recursively within the same singleton class.
        Returns:
            Self: The singleton instance.
        """
        working_classes = _get_tls_working_classes()
        if cls in working_classes:
            raise SelfRecursiveReferenceError("Circular reference detected")

        metadata = _get_metadata(cls)

        if working_classes:
            logger.error(
                "[Singleton] Strict mode: Calling %s.instance() " "within %s is not allowed.",
                cls.__name__,
                " -> ".join(base.__name__ + "()" for base in working_classes),
            )
            raise DependencyInjectionViolationError("Dependency injection violation")

        # Return the object if success
        with metadata.singleton_lock:
            if metadata.state == SingletonFactoryState.SUCCESS:
                # Already initialized, return the instance
                return metadata.instance.result()

        # Periodically logger if we need to wait for it
        periodic = 5.0
        while timeout is None or timeout > 0:
            wait_time = min(timeout, periodic) if timeout else periodic
            try:
                return metadata.instance.result(timeout=wait_time)
            except ct.TimeoutError:
                with metadata.singleton_lock:
                    if metadata.state == SingletonFactoryState.WORKING:
                        logger.info(
                            "[Singleton] thread %s is still waiting for %s to be initialized.",
                            threading.current_thread().name,
                            cls.__name__,
                        )
                    elif metadata.state == SingletonFactoryState.IDLE:
                        logger.warning(
                            "[Singleton] thread %s hangs at %s.instance(). "
                            "Waiting for another thread to initialize %s().",
                            threading.current_thread().name,
                            cls.__name__,
                            cls.__name__,
                        )
            if timeout:
                timeout -= wait_time
        return metadata.instance.result(timeout=timeout)

    @classmethod
    @final
    def initialized(cls) -> bool:
        """Check if the singleton instance is initialized."""
        metadata = _get_metadata(cls)
        with metadata.singleton_lock:
            return metadata.state == SingletonFactoryState.SUCCESS


def reset_singleton(cls: type[Singleton], warning: bool = True) -> None:
    """Reset the singleton instance for testing purpose only.

    Args:
        cls (type[Singleton]): The singleton class to reset.
    """
    # check and warning if not in pytest
    if warning and "PYTEST_CURRENT_TEST" not in os.environ:
        logger.warning(
            "[Singleton] reset_singleton called outside pytest environment. "
            "This may lead to unexpected behaviors."
        )

    metadata = _get_metadata(cls)
    # only for testing, don't directly use it in production code
    # recursively reset the singletons whose ownership is cls
    for subclass in list(metadata.owned_singletons):
        reset_singleton(subclass, warning=warning)

    with metadata.singleton_lock:
        metadata.state = SingletonFactoryState.IDLE
        metadata.instance = ct.Future()
        metadata.owned_singletons.clear()


class SingletonError(RuntimeError): ...


class ManyConstructionError(SingletonError): ...


class DependencyInjectionViolationError(SingletonError): ...


class SelfRecursiveConstructionError(SingletonError): ...


class SelfRecursiveReferenceError(SingletonError): ...
