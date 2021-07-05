from fastapi import HTTPException, status

InvalidCredentials = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Incorrect username or password',
    headers={'WWW-Authenticate': 'Basic'},
)

UserAlreadyExists = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail='User already exists',
)

UserNotFound = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail='User was not found',
)

FilmNotFound = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail='Film was not found',
)

FilmAlreadyExists = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail='Film already exists',
)

InternalError = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail='Some internal error occurred',
)

ForbiddenAction = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail='You are not allowed to do this action',
)

InvalidReview = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail='Invalid review data',
)
