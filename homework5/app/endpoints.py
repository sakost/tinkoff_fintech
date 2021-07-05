from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .auth import auth_required
from .config import get_settings
from .db import Film, Review, User, UserRole
from .deps import get_current_user, get_db, get_user_role
from .exceptions import (
    FilmAlreadyExists,
    ForbiddenAction,
    InvalidReview,
    UserAlreadyExists,
    UserNotFound,
)
from .schemas import (
    FilmCreate,
    FilmGet,
    FilmModel,
    HTTPError,
    Paginate,
    ResponseModel,
    ReviewCreate,
    ReviewGet,
    UserCreate,
    UserGet,
)
from .utils import paginate_query

router = APIRouter()


@router.post(
    '/users',
    response_model=ResponseModel,
    responses={
        UserAlreadyExists.status_code: {
            'model': HTTPError,
            'description': UserAlreadyExists.detail,
        },
    },
    tags=['users', 'auth'],
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db),
    user_role: UserRole = Depends(get_user_role),
) -> Any:
    """
    Register user
    """
    db_user = User(name=user.name, role=user_role)
    db_user.set_password(user.password)
    try:
        db.add(db_user)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise UserAlreadyExists  # pylint: disable=raise-missing-from

    return {
        'status': 'ok',
        'data': UserGet.from_orm(db_user),
    }


@router.get('/users/me', response_model=ResponseModel, tags=['users'])
def get_logged_user(current_user: User = Depends(get_current_user)) -> Any:
    """
    Returns information about logged in user
    """
    return {
        'status': 'ok',
        'data': UserGet.from_orm(current_user),
    }


@router.get(
    '/users/{user_id}',
    response_model=ResponseModel,
    responses={
        UserNotFound.status_code: {
            'model': HTTPError,
            'description': UserNotFound.detail,
        },
    },
    tags=['users'],
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_required),  # pylint: disable=unused-argument
) -> Any:
    """
    Returns information about given user
    """
    searched_user = db.query(User).get(user_id)
    if not searched_user:
        raise UserNotFound
    return {
        'status': 'ok',
        'data': UserGet.from_orm(searched_user),
    }


@router.post(
    '/films',
    response_model=ResponseModel,
    responses={
        ForbiddenAction.status_code: {
            'model': HTTPError,
            'description': ForbiddenAction.detail,
        },
        FilmAlreadyExists.status_code: {
            'model': HTTPError,
            'description': FilmAlreadyExists.detail,
        },
    },
    tags=['films', 'admins'],
)
def add_film(
    film: FilmCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Any:
    """
    Add new film
    """
    if not user.role.can_add_films:
        raise ForbiddenAction

    db_film = db.query(Film).filter(Film.name == film.name).first()
    if db_film is not None:
        raise FilmAlreadyExists

    db_film = Film(
        name=film.name,
        released_year=film.released_year,
        owner_user=user,
    )

    db.add(db_film)
    db.flush()
    film_model = FilmGet.from_orm(db_film)
    db.commit()
    return {
        'status': 'ok',
        'data': film_model,
    }


@router.get('/films', response_model=ResponseModel)
def get_films(
    film: FilmModel,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),  # pylint: disable=unused-argument
) -> Any:
    """
    List films
    """
    filters = []
    if film.filter_by_text:
        filters.append(Film.name.contains(film.filter_by_text))
    if film.filter_by_year:
        filters.append(Film.released_year == film.filter_by_year)
    db_films_query = db.query(Film).filter(*filters)
    if film.sort_by_avg_score:
        db_films_query = db_films_query.order_by(Film.avg_review_rate.desc())
    db_films_query = paginate_query(
        db_films_query, film.page, get_settings().OBJECTS_PER_PAGE
    )

    db_films = db_films_query.all()

    films = list(map(FilmGet.from_orm, db_films))
    return {
        'status': 'ok',
        'data': films,
    }


@router.post('/reviews', response_model=ResponseModel)
def add_review(
    review: ReviewCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Any:
    db_review = Review(
        film_id=review.film_id,
        user=user,
        score=review.score,
        text=review.text,
    )
    try:
        db.add(db_review)
        db.flush()
        added_review = ReviewGet.from_orm(db_review)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise InvalidReview  # pylint: disable=raise-missing-from
    return {
        'status': 'ok',
        'data': added_review,
    }


@router.get('/reviews', response_model=ResponseModel)
def get_reviews(
    pagination: Paginate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Any:
    reviews_query = db.query(Review).filter(Review.user_id == user.id)
    reviews_query = paginate_query(
        reviews_query, pagination.page, get_settings().OBJECTS_PER_PAGE
    )
    reviews = reviews_query.all()
    return {
        'status': 'ok',
        'data': list(
            map(
                ReviewGet.from_orm,
                reviews,
            )
        ),
    }
