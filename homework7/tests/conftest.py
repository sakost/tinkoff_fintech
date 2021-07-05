# pylint: disable=unused-argument,broad-except
from concurrent.futures import Executor, Future
from threading import Lock
from typing import Any

import pytest


class DummyExecutor(Executor):
    def __init__(self):
        self._shutdown = False
        self._shutdownLock = Lock()
        self._fn = None

    def submit(self, fn, /, *args: Any, **kwargs: Any):
        with self._shutdownLock:
            if self._shutdown:
                raise RuntimeError('cannot schedule new futures after shutdown')

            f = Future()  # type: ignore[var-annotated]
            try:
                result = fn(*args, **kwargs)
            except Exception as e:
                f.set_exception(e)
            else:
                f.set_result(result)

            return f

    def shutdown(self, wait: bool = True, *, cancel_futures: bool = False):
        with self._shutdownLock:
            self._shutdown = True


@pytest.fixture(scope='session')
def dummy_executor() -> DummyExecutor:
    return DummyExecutor()
