from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.recommendation import RecommendationResponse, RecommendationItem
from app.services.auth_service import get_current_user
from app.services.hybrid_engine import hybrid_engine

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


@router.get("", response_model=RecommendationResponse)
def get_recommendations(
    top_n: int = Query(20, ge=1, le=50),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return hybrid_engine.recommend(user.id, db, top_n=top_n)


@router.get("/similar/{movie_id}", response_model=list[RecommendationItem])
def get_similar_movies(
    movie_id: int,
    top_n: int = Query(10, ge=1, le=30),
    db: Session = Depends(get_db),
):
    return hybrid_engine.get_similar_movies(movie_id, db, top_n=top_n)
