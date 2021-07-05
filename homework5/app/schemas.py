from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel, Field


class StatusType(Enum):
    OK = 'ok'
    ERROR = 'error'


class Paginate(BaseModel):
    page: int = Field(default=1, gt=0)


class UserBase(BaseModel):
    name: str


class UserCreate(UserBase):
    password: str


class UserInDBBase(UserBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


class User(UserInDBBase):
    pass


class UserGet(User):
    pass


class UserPost(UserBase):
    pass


class UserInDB(UserInDBBase):
    password_hash: str


class FilmBase(BaseModel):
    id: Optional[int]


class FilmCreate(FilmBase):
    # first ever film was released at 1878 year
    released_year: int = Field(ge=1878)
    name: str = Field(max_length=128, min_length=1)


class FilmInDBBase(FilmCreate):
    class Config:
        orm_mode = True


class FilmModel(FilmBase, Paginate):
    filter_by_text: Optional[str] = ''
    filter_by_year: Optional[int]
    sort_by_avg_score: Optional[bool] = False


class FilmInDB(FilmInDBBase):
    avg_rate: Optional[float]
    count_reviews: int = Field(ge=0)


class FilmGet(FilmInDB):
    pass


class FilmPost(FilmBase):
    pass


class HTTPError(BaseModel):
    detail: str

    class Config:
        schema_extra = {
            'example': {
                'detail': 'HTTPException raised.',
            }
        }


class ReviewBase(BaseModel):
    pass


class ReviewModel(ReviewBase, Paginate):
    pass


class ReviewCreate(ReviewBase):
    film_id: int
    score: int = Field(ge=0, le=10)
    text: Optional[str]


class ReviewGet(ReviewCreate):
    class Config:
        orm_mode = True


class ResponseModel(BaseModel):
    status: StatusType
    data: Optional[Union[UserGet, FilmGet, list[FilmGet], ReviewGet, list[ReviewGet]]]
    error: Optional[str]
