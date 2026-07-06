from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session, joinedload
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database import get_db
from app.models.movie import Movie
from app.models.user import User
from app.schemas.movie import MovieBrief
from app.schemas.recommendation import ChatRequest, ChatResponse
from app.services.auth_service import get_current_user
from app.services.gemini_service import gemini_service

router = APIRouter(prefix="/api/chat", tags=["chat"])
limiter = Limiter(key_func=get_remote_address)


@router.post("", response_model=ChatResponse)
@limiter.limit("10/minute")
def chat_recommend(
    request: Request,
    data: ChatRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    history = [{"role": m.role, "content": m.content} for m in data.history]

    reply, movie_ids = gemini_service.chat(
        message=data.message,
        history=history,
        user_id=user.id,
        db=db,
    )

    # Fetch matched movies
    recommended_movies = []
    if movie_ids:
        movies = (
            db.query(Movie)
            .options(joinedload(Movie.genres))
            .filter(Movie.id.in_(movie_ids))
            .all()
        )
        recommended_movies = [MovieBrief.model_validate(m) for m in movies]

    return ChatResponse(reply=reply, recommended_movies=recommended_movies)
