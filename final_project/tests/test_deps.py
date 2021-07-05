from unittest import mock

import pytest

from app.deps import get_db


def test_get_db():
    def _tmp():
        raise Exception()

    with mock.patch('app.deps.SessionLocal') as patched:
        patched.return_value = patched
        patched.commit = _tmp
        coro = get_db()
        assert coro.send(None) == patched
        with pytest.raises(Exception):
            coro.send(None)
        assert patched.close.call_count == 1
        assert patched.rollback.call_count == 1
