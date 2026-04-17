from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.rating import Rating
from app.schemas.user import UserCreate, UserOut, Token, LoginRequest, RatingCreate, RatingOut
from app.services.auth_service import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/users", tags=["users"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
@limiter.limit("3/minute")
def register(request: Request, data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(
        (User.username == data.username) | (User.email == data.email)
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="An account with this username or email already exists.",
        )

    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
def login(request: Request, data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token)


@router.get("/me", response_model=UserOut)
def get_me(user: User = Depends(get_current_user)):
    return user


@router.post("/ratings", response_model=RatingOut, status_code=status.HTTP_201_CREATED)
def rate_movie(
    data: RatingCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not (0.5 <= data.score <= 5.0):
        raise HTTPException(status_code=400, detail="Score must be between 0.5 and 5.0")

    existing = db.query(Rating).filter(
        Rating.user_id == user.id, Rating.movie_id == data.movie_id
    ).first()

    if existing:
        existing.score = data.score
        db.commit()
        db.refresh(existing)
        return existing

    rating = Rating(user_id=user.id, movie_id=data.movie_id, score=data.score)
    db.add(rating)
    db.commit()
    db.refresh(rating)
    return rating


@router.get("/ratings", response_model=list[RatingOut])
def get_my_ratings(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Rating).filter(Rating.user_id == user.id).all()
