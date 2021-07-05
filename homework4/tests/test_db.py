from unittest.mock import patch

import pytest
from flask import Flask


def test_scoped_db_session(app: Flask) -> None:
    with app.db_session() as session:
        session_id = id(session)
    with app.db_session() as session:
        assert session_id == id(session)


def test_commit_db(app: Flask) -> None:
    with patch('app.database.Session') as mocked_Session:
        mocked_Session.return_value = mocked_Session
        with app.db_session():
            pass
        assert mocked_Session.commit.call_count == 1
        assert mocked_Session.close.call_count == 1


def test_rollback_db(app: Flask) -> None:
    with patch('app.database.Session') as mocked_Session:
        mocked_Session.return_value = mocked_Session
        with pytest.raises(Exception), app.db_session():
            raise Exception()
        assert mocked_Session.commit.call_count == 0
        assert mocked_Session.rollback.call_count == 1
        assert mocked_Session.close.call_count == 1
