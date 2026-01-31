"""Testable Singleton class with Dependency Injection enforcement.

Doc: https://bytedance.us.larkoffice.com/docx/I9EsdRJM3ou2JaxVv1Ku63vSs9e

The metadata and states to manage singleton instances are stored under the module
of the singleton class, so that different singleton classes in different modules
do not interfere with each other.

ContextVars are used to track the construction and execution stack of singleton classes,
so that we can enforce Dependency Injection principles and prevent self-recursive
construction and reference.

### A few Definitions used in this module
- Instantiation: Creating a new object. e.g. `MyClass() -> calls __new__`
- Initialization: Setting up the object after instantiation. e.g. `MyClass.__init__()`
- Construction: The informal term of "Instantiation + Initialization". e.g. `MyClass()`

### Reference
Check out Google's 2008 Talk and Blog on "Global State and Singletons".
- https://bilibili.com/video/BV1mt4y12799/
- https://youtu.be/-FRm3VPhseI?si=S4q1MNzAejAf1_AZ
- https://testing.googleblog.com/2008/08/root-cause-of-singletons.html
"""

from __future__ import annotations

import enum
import functools
import logging
import os
import sys
import threading
from abc import ABC, ABCMeta
from concurrent import futures as cf
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Any, Callable, Self, cast, final

__all__ = ["Singleton", "SingletonMeta", "reset_singleton"]

logger = logging.getLogger(__name__)

_CONSTRUCTING: ContextVar[tuple[type["Singleton"], ...]] = ContextVar("_CONSTRUCTING", default=())
_EXEC_STACK: ContextVar[tuple[type["Singleton"], ...]] = ContextVar("_EXEC_STACK", default=())


class SingletonFactoryState(enum.Enum):
    """The state of the singleton factory."""

    IDLE = enum.auto()
    WORKING = enum.auto()
    SUCCESS = enum.auto()
    FAILED = enum.auto()


def _exec_stack_wrapper(func) -> Callable[[Any], Any]:
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        cls = type(self)
        stack = _EXEC_STACK.get()
        token = _EXEC_STACK.set(stack + (cls,))
        logger.debug(
            "Entering %s.%s, execution stack: %s",
            cls.__name__,
            func.__name__,
            [e for e in stack + (cls,)],
        )
        try:
            return func(self, *args, **kwargs)
        finally:
            _EXEC_STACK.reset(token)

    return wrapper


@dataclass
class SingletonMetadata:
    """Metadata for managing singleton instances and their state."""

    instance: cf.Future = field(default_factory=cf.Future)
    state: SingletonFactoryState = SingletonFactoryState.IDLE

    # ! Note that it's safe to acquire this lock even in asyncio
    singleton_lock: threading.Lock = field(default_factory=threading.Lock)

    # Singleton A owns Singleton B if A constructs B during its initialization
    # so in tests we can clean up B when A is reset.
    owns: set[type[Singleton]] = field(default_factory=set)

    # Singleton A depends on Singleton B if A holds a reference to B
    # so that when `.instance()` is called on A, we can check for Dependency Injection violation.
    depends: set[type[Singleton]] = field(default_factory=set)


def _get_meta_dict(
    cls: type[Singleton], init: bool = False
) -> dict[type[Singleton], SingletonMetadata]:
    """Get or create the singleton metadata dict under the module of cls."""
    module = sys.modules[cls.__module__]
    if not hasattr(module, "__singleton_meta_dict__"):
        if init:
            setattr(module, "__singleton_meta_dict__", {})
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
    """Singleton metaclass to enforce singleton behavior."""

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

        constructing = _CONSTRUCTING.get()
        if _cls in constructing:
            raise SelfRecursiveConstructionError("Circular construction detected")

        metadata = _get_metadata(_cls)

        # This is the construction
        is_root_owner = not constructing
        # The token is a python ContextVar feature
        # see https://docs.python.org/3/library/contextvars.html#contextvars.ContextVar.reset
        token = _CONSTRUCTING.set(constructing + (_cls,))
        try:
            # Check if a non-leaf class is initialized
            with metadata.singleton_lock:
                if metadata.state in [
                    SingletonFactoryState.WORKING,
                    SingletonFactoryState.SUCCESS,
                ]:
                    raise ManyConstructionError(f"{_cls.__name__} already initialized")

                if metadata.state == SingletonFactoryState.FAILED:
                    metadata.instance = cf.Future()
                metadata.state = SingletonFactoryState.WORKING
            if not is_root_owner:
                # Track ownership for classes, so that we can clean up properly in tests
                _get_metadata(constructing[-1]).owns.add(_cls)

            # Release the lock and then do block initialization
            try:
                # cls.__init__() is called inside super().__call__()
                # so this line of code is instantiate and initialize the singleton instance.
                instance = super().__call__(*args, **kwargs)
                instance = cast("Singleton", instance)

            # catch BaseException here because SystemExit and KeyboardInterrupt also need to be
            # handled
            except BaseException as e:
                with metadata.singleton_lock:
                    metadata.state = SingletonFactoryState.FAILED
                    metadata.instance.set_exception(e)

                    if metadata.owns:
                        # ! It's not safe to automatically clean up owned singletons here,
                        # ! because other threads may be using them.
                        logger.critical(
                            "[Singleton] Critical: Singleton %s failed to initialize, "
                            "but it owns other singletons: [%s]. "
                            "These singletons may be leaked and need manual cleanup.",
                            cls.__name__,
                            ", ".join(s.__name__ for s in metadata.owns),
                        )
                raise e
            with metadata.singleton_lock:
                metadata.state = SingletonFactoryState.SUCCESS
                metadata.instance.set_result(instance)

                # record the dependencies
                # ! This doesn't work if the attribute is first set with None and then assigned
                # ! later. Please avoid such patterns in singleton classes,
                # e.g. `A(dep=None); A.instance().dep = B.instance()`
                # Do it recursively as DFS
                stack = [instance]
                visited: set[type["Singleton"]] = set([_cls])
                while stack:
                    curr = stack.pop()
                    for attr_name in curr.__dict__.values():

                        if isinstance(attr_name, Singleton):
                            dep_cls = type(attr_name)
                            if dep_cls not in visited:
                                dep_metadata = _get_metadata(dep_cls)

                                # Two-phase locking
                                with dep_metadata.singleton_lock:
                                    # assert the dependency is initialized
                                    if dep_metadata.state != SingletonFactoryState.SUCCESS:
                                        raise DependencyInjectionViolationError(
                                            f"Dependency {dep_cls.__name__} is not initialized! "
                                            "This may be caused by partial initialization."
                                        )
                                metadata.depends.add(dep_cls)
                                stack.append(attr_name)
                                visited.add(dep_cls)
                if metadata.owns:
                    logger.debug(
                        "[Singleton] %s owns: [%s]",
                        cls.__name__,
                        ", ".join(s.__name__ for s in metadata.owns),
                    )
                logger.debug(
                    "[Singleton] %s depends on: [%s]",
                    cls.__name__,
                    ", ".join(s.__name__ for s in metadata.depends),
                )
            return instance
        finally:
            _CONSTRUCTING.reset(token)

    def __new__(mcs, name, bases, namespace, **kwargs):
        """Wrap methods to track execution stack for Dependency Injection enforcement."""
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)

        for attr_name, attr in namespace.items():
            if not callable(attr):
                continue
            if isinstance(attr, (staticmethod, classmethod)):
                continue
            if attr_name.startswith("__") and attr_name.endswith("__"):
                if attr_name != "__call__":
                    # skip dunder methods
                    continue

            logger.debug("Wrapping %s.%s to track execution stack", name, attr_name)
            setattr(cls, attr_name, _exec_stack_wrapper(attr))
        return cls


class Singleton(ABC, metaclass=SingletonMeta):
    """Testable Thread-safe Singleton class

    https://bytedance.us.larkoffice.com/docx/I9EsdRJM3ou2JaxVv1Ku63vSs9e

    - Supports subclassing, @dataclass, and type hinting.
        - ***Note that since Singleton is thread-safe and supports subclassing, all sub-classes of \
            Singleton must also be thread safe.***
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

    # If Singleton A depends Singleton B, it must be stated explicitly.
    class MyDependentSingleton(Singleton):
        def __init__(self, dependency: MySingleton):
            # self.dependency = MySingleton.instance() raises RuntimeError.
            self.dependency = dependency

    # ! Please avoid initialize an attribute with None and then assign it later.
    # ! Doing so prevents correct detection of dependencies.
    class SomeOtherSingleton(Singleton):
        dep: MySingleton

    # ! Avoid doing this:
    SomeOtherSingleton(dep=None); SomeOtherSingleton.instance().dep = MySingleton.instance()

    # Calling B.instance() within A's method is prohibited and raises
    # DependencyInjectionViolationError.
    # A reference of B must be passed to A during A's construction.
    class SomeBaseSingletonClass(Singleton):
        def do_something(self):
            SomeOtherSingleton.instance()  # raises DependencyInjectionViolationError

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
        - then in any method of class B, all locks must be acquired in the order \
            la1 -> la2 -> lb2 -> lb1
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
            cf.TimeoutError: If the instance is not ready within the timeout.
            DependencyInjectionViolationError: If called within the construction of another
                singleton.
            SelfRecursiveReferenceError: If called recursively within the same singleton class.
        Returns:
            Self: The singleton instance.
        """

        # 1. Check for self-recursive reference
        constructing = _CONSTRUCTING.get()
        if cls in constructing:
            raise SelfRecursiveReferenceError("Circular reference detected")

        # 2. Check for Dependency Injection violation in Construction Stack
        metadata = _get_metadata(cls)
        if constructing:
            logger.error(
                "[Singleton] Strict mode: Calling %s.instance() " "within %s is not allowed.",
                cls.__name__,
                " -> ".join(base.__name__ + "()" for base in constructing),
            )
            raise DependencyInjectionViolationError("Dependency injection violation")

        # 3. Check for Dependency Injection violation in Execution Stack
        exec_stack = _EXEC_STACK.get()
        logger.debug(
            "Singleton %s.instance() called within execution stack: %s",
            cls.__name__,
            exec_stack,
        )
        if exec_stack:
            caller = exec_stack[-1]
            caller_metadata = _get_metadata(caller)
            if cls != caller and cls not in caller_metadata.depends:
                logger.error(
                    "[Singleton] Strict mode: Calling %s.instance() within %s "
                    "is not allowed. "
                    "Please pass the instance of %s into %s's __init__() instead.",
                    cls.__name__,
                    " -> ".join(base.__name__ + "()" for base in exec_stack),
                    cls.__name__,
                    caller.__name__,
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
            except cf.TimeoutError:
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
    for subclass in list(metadata.owns):
        reset_singleton(subclass, warning=warning)

    with metadata.singleton_lock:
        metadata.state = SingletonFactoryState.IDLE
        metadata.instance = cf.Future()
        metadata.owns.clear()
        metadata.depends.clear()


class SingletonError(RuntimeError):
    """Base class for Singleton related errors."""


class ManyConstructionError(SingletonError):
    """Raised when attempting to construct a singleton more than once."""


class DependencyInjectionViolationError(SingletonError):
    """Raised when dependency injection principles are violated."""


class SelfRecursiveConstructionError(SingletonError):
    """Raised when a singleton attempts to construct itself recursively."""


class SelfRecursiveReferenceError(SingletonError):
    """Raised when a singleton attempts to reference itself recursively."""
