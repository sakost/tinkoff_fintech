# pylint: disable=unused-argument
from base64 import b64encode
from http import HTTPStatus
from typing import Optional

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.models import Film, Review, User


def modify_headers_for_auth(
    headers: dict[str, str], login: str, password: str
) -> dict[str, str]:
    headers['Authorization'] = (
        'Basic ' + b64encode(f'{login}:{password}'.encode()).decode()
    )
    return headers


def test_success_reg_user(client: TestClient) -> None:
    response = client.post(
        '/users',
        json={
            'name': 'username',
            'password': 'asdf',
        },
    )

    assert response.status_code == HTTPStatus.OK
    response_json = response.json()
    assert response_json['status'] == 'ok'
    assert response_json['data']['name'] == 'username'


def test_fail_reg_user(user: User, client: TestClient) -> None:
    response = client.post(
        '/users',
        json={
            'name': 'user',
            'password': 'password',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'User already exists'}


def test_success_get_me(client: TestClient, user: User) -> None:
    response = client.get(
        '/users/me', headers=modify_headers_for_auth({}, 'user', 'password')
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'data': {'id': 2, 'name': 'user'},
        'error': None,
        'status': 'ok',
    }


def test_fail_password_get_me(client: TestClient, user: User) -> None:
    response = client.get(
        '/users/me', headers=modify_headers_for_auth({}, 'user', 'not password')
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {
        'detail': 'Incorrect username or password',
    }


def test_fail_username_get_me(client: TestClient, user: User) -> None:
    response = client.get(
        '/users/me', headers=modify_headers_for_auth({}, 'not user', 'password')
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {
        'detail': 'Incorrect username or password',
    }


def test_success_get_user(client: TestClient, user: User) -> None:
    response = client.get(
        '/users/2', headers=modify_headers_for_auth({}, 'user', 'password')
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'error': None,
        'status': 'ok',
        'data': {
            'id': 2,
            'name': 'user',
        },
    }


def test_fail_get_user(client: TestClient, user: User) -> None:
    response = client.get(
        '/users/200', headers=modify_headers_for_auth({}, 'user', 'password')
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {
        'detail': 'User was not found',
    }


def test_not_allowed_add_films(client: TestClient, user: User) -> None:
    response = client.post(
        '/films',
        json={
            'released_year': 1900,
            'name': 'some film name',
        },
        headers=modify_headers_for_auth({}, 'user', 'password'),
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {
        'detail': 'You are not allowed to do this action',
    }


def test_film_already_exists_add_films(client: TestClient, film: Film) -> None:
    response = client.post(
        '/films',
        json={
            'released_year': 1900,
            'name': 'film',
        },
        headers=modify_headers_for_auth({}, 'admin', 'admin'),
    )
    assert response.status_code == HTTPStatus.CONFLICT


def test_success_add_films(client: TestClient) -> None:
    response = client.post(
        '/films',
        json={
            'released_year': 1900,
            'name': 'some film name',
        },
        headers=modify_headers_for_auth({}, 'admin', 'admin'),
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'status': 'ok',
        'error': None,
        'data': {
            'name': 'some film name',
            'id': 1,
        },
    }


def test_get_films(client: TestClient, film: Film) -> None:
    response = client.get(
        '/films', headers=modify_headers_for_auth({}, 'admin', 'admin'), json={}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'data': [
            {
                'avg_rate': None,
                'count_reviews': 0,
                'id': 1,
                'name': 'film',
                'released_year': 2000,
            }
        ],
        'error': None,
        'status': 'ok',
    }


@pytest.mark.parametrize(
    'score,text',
    [
        [10, 'some text'],
        [0, None],
    ],  # pylint: disable=too-many-arguments
)
def test_success_add_review(
    score: int,
    text: Optional[str],
    db_session: Session,
    client: TestClient,
    film: Film,
    admin: User,
) -> None:
    response = client.post(
        '/reviews',
        json={
            'film_id': film.id,
            'score': score,
            'text': text,
        },
        headers=modify_headers_for_auth({}, 'admin', 'admin'),
    )

    assert response.status_code == HTTPStatus.OK
    review = db_session.query(Review).filter_by(film_id=film.id, user=admin).one()
    assert review.text == text
    assert review.score == score


def test_fail_add_review(client: TestClient, film: Film, review: Review) -> None:
    response = client.post(
        '/reviews',
        json={
            'film_id': film.id,
            'score': 0,
            'text': None,
        },
        headers=modify_headers_for_auth({}, 'admin', 'admin'),
    )

    assert response.status_code == HTTPStatus.CONFLICT


def test_get_reviews(client: TestClient, review: Review) -> None:
    response = client.get(
        '/reviews', headers=modify_headers_for_auth({}, 'admin', 'admin'), json={}
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'data': [{'film_id': 1, 'score': 5, 'text': 'text'}],
        'error': None,
        'status': 'ok',
    }
