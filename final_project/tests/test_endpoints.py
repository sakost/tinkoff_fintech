from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.models import Book, User


def test_get_books(client: TestClient, book) -> None:
    response = client.get(f'/{book.owner.id}/books')
    data = response.json()

    assert data[0]['text'] == book.text
    assert data[0]['title'] == book.title


def test_add_book(client: TestClient, user: User, db_session: Session) -> None:
    response = client.post(
        f'/{user.id}/books',
        json={
            'title': '1111',
            'text': 'texxt',
            'owner': {
                'name': user.name,
                'id': user.id,
            },
        },
    )

    assert response.json()['status'] == 'ok'
    text = db_session.query(Book).filter(Book.owner_id == user.id).one_or_none()
    assert text is not None
    assert text.text == 'texxt'
    assert text.title == '1111'


def test_register_user(client: TestClient, db_session: Session):
    response = client.post(
        '/user',
        json={
            'name': 'some_username',
        },
    )
    assert response.json()['status'] == 'ok'
    user = db_session.query(User).filter(User.name == 'some_username').one_or_none()
    assert user is not None
    assert user.name == 'some_username'


def test_get_user(client: TestClient, user: User):
    response = client.get(f'/user/{user.id}')
    data = response.json()
    assert data['id'] == user.id
    assert data['name'] == user.name
