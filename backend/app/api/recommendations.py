"""Recommendations powered by TMDB API + user ratings (no local ML models)."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.movie import Movie
from app.models.rating import Rating
from app.models.user import User
from app.schemas.movie import MovieBrief
from app.schemas.recommendation import RecommendationResponse, RecommendationItem
from app.services.auth_service import get_current_user
from app.services.tmdb_service import tmdb_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


def _tmdb_item_to_brief(item: dict, rank: int) -> MovieBrief:
    """Convert a raw TMDB result dict into a MovieBrief (no DB lookup)."""
    return MovieBrief(
        id=-(rank + 1),  # negative sentinel — not in local DB
        tmdb_id=item.get("id", 0),
        title=item.get("title") or item.get("name") or "Unknown",
        vote_average=float(item.get("vote_average") or 0),
        poster_path=item.get("poster_path") or "",
        release_date=item.get("release_date") or item.get("first_air_date") or "",
        genres=[],
    )


@router.get("", response_model=RecommendationResponse)
def get_recommendations(
    top_n: int = Query(20, ge=1, le=50),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Personalized recommendations.

    Strategy:
    1. If the user has rated movies, use their top-rated movies' TMDB IDs to
       fetch TMDB recommendations for each, then merge & deduplicate.
    2. If no ratings, fall back to TMDB trending/popular.
    """
    # Get user's top-rated movies
    user_ratings = (
        db.query(Rating)
        .options(joinedload(Rating.movie))
        .filter(Rating.user_id == user.id)
        .order_by(Rating.score.desc())
        .limit(10)
        .all()
    )

    liked = [r for r in user_ratings if r.score >= 3.5 and r.movie and r.movie.tmdb_id]

    if liked:
        # Fetch TMDB recommendations seeded by each liked movie
        seen_tmdb_ids: set[int] = set()
        rated_tmdb_ids = {r.movie.tmdb_id for r in user_ratings if r.movie}
        all_items: list[RecommendationItem] = []

        for r in liked[:5]:  # top 5 liked movies
            recs = tmdb_service.get_recommendations_tmdb(r.movie.tmdb_id)
            for i, item in enumerate(recs):
                tmdb_id = item.get("id")
                if not tmdb_id or tmdb_id in seen_tmdb_ids or tmdb_id in rated_tmdb_ids:
                    continue
                seen_tmdb_ids.add(tmdb_id)
                score = float(item.get("vote_average", 0)) / 10.0
                all_items.append(
                    RecommendationItem(
                        movie=_tmdb_item_to_brief(item, len(all_items)),
                        score=round(score, 4),
                        reason=f"Because you liked {r.movie.title}",
                    )
                )
                if len(all_items) >= top_n:
                    break
            if len(all_items) >= top_n:
                break

        if all_items:
            # Sort by score descending
            all_items.sort(key=lambda x: x.score, reverse=True)
            return RecommendationResponse(
                recommendations=all_items[:top_n], strategy="personalized"
            )

    # Fallback: trending movies
    trending = tmdb_service.get_trending_week()
    items = []
    for i, item in enumerate(trending[:top_n]):
        score = float(item.get("vote_average", 0)) / 10.0
        items.append(
            RecommendationItem(
                movie=_tmdb_item_to_brief(item, i),
                score=round(score, 4),
                reason="Trending this week",
            )
        )

    return RecommendationResponse(recommendations=items, strategy="trending")


@router.get("/similar/{movie_id}", response_model=list[RecommendationItem])
def get_similar_movies(
    movie_id: int,
    top_n: int = Query(10, ge=1, le=30),
    db: Session = Depends(get_db),
):
    """Get similar movies via TMDB API."""
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    results = tmdb_service.get_similar_tmdb(movie.tmdb_id)
    items = []
    for i, item in enumerate(results[:top_n]):
        score = float(item.get("vote_average", 0)) / 10.0
        items.append(
            RecommendationItem(
                movie=_tmdb_item_to_brief(item, i),
                score=round(score, 4),
                reason=f"Similar to {movie.title}",
            )
        )
    return items
