# pylint: disable=unused-argument
from http import HTTPStatus

from flask import request, url_for

import todo_list.app
import todo_list.models
import todo_list.views


def test_index_redirect(client):
    response = client.get('/')
    assert response.status_code == HTTPStatus.FOUND
    assert response.headers['Location'] == 'http://localhost/tasks'


def test_no_tasks(client):
    response = client.get('/tasks')
    assert 'No tasks' in response.data.decode()


def test_successfully_add_task_status_code(client, db_session):
    assert (
        client.post('/new_task', data={'task_description': 'text'}).status_code
        == HTTPStatus.FOUND
    )


def test_successfully_add_task(app, client, db_session):
    with client:
        response = client.post(
            '/new_task', data={'task_description': 'text'}, follow_redirects=True
        )
        response_data = response.data.decode()
        assert 'text' in response_data
        assert app.config['TASK_SUCCESSFULLY_ADDED_MESSAGE'] in response_data
        assert request.path == url_for('view.tasks')
    assert db_session.query(todo_list.models.Task).count() == 1


def test_get_request_add_task_status_code(client):
    assert client.get('/new_task').status_code == HTTPStatus.OK


def test_fail_add_task(app, client):
    assert (
        client.post('/new_task').status_code == HTTPStatus.FOUND
    )  # redirect to /tasks

    response = client.post('/new_task', follow_redirects=True)
    assert app.config['EMPTY_TASK_MESSAGE'] in response.data.decode()


def test_invalid_id_done_task(client, db_session):
    db_session.add(todo_list.models.Task(id=1, description='text1'))
    db_session.add(todo_list.models.Task(id=2, description='text2', done=True))
    db_session.commit()
    with client:
        assert (
            client.get(url_for('view.done_task', task_id=10)).status_code
            == HTTPStatus.NOT_FOUND
        )
        assert (
            client.get(url_for('view.done_task', task_id=2)).status_code
            == HTTPStatus.NOT_FOUND
        )


def test_done_task(client, db_session):
    assert client.get('/done_task').status_code == HTTPStatus.NOT_FOUND

    db_session.add(todo_list.models.Task(id=1, description='text1'))
    db_session.add(todo_list.models.Task(id=2, description='text2'))
    db_session.commit()

    with client:
        assert (
            client.get(url_for('view.done_task', task_id=1)).status_code
            == HTTPStatus.FOUND
        )

        response = client.get(
            url_for('view.done_task', task_id=2, filter='text2', status='all'),
            follow_redirects=True,
        )
        assert 'disabled' in response.data.decode()

    assert (
        db_session.query(todo_list.models.Task)
        .filter(todo_list.models.Task.done == 1)
        .count()
        == 2
    )
