from fastapi import HTTPException, status

InternalError = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail='Some internal error occurred',
)

ForbiddenAction = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail='You are not allowed to do this action',
)

UserAlreadyExists = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail='User already exists',
)

BookAlreadyExists = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail='Book with such title already exists',
)

UserNotFound = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail='User was not found',
)
