from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: str
    password: str


class RatingCreate(BaseModel):
    movie_id: int
    score: float  # 0.5 to 5.0


class RatingOut(BaseModel):
    id: int
    movie_id: int
    score: float

    model_config = {"from_attributes": True}
