from http import HTTPStatus

from fastapi import HTTPException

InvalidTaskId = HTTPException(
    detail='Invalid task id',
    status_code=HTTPStatus.NOT_FOUND,
)

InvalidTaskStatus = HTTPException(
    detail='Invalid task status',
    status_code=HTTPStatus.EXPECTATION_FAILED,
)
