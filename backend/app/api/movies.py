import json
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from app.config import get_settings
from app.database import get_db
from app.models.movie import Movie, Genre
from app.schemas.movie import MovieOut, MovieBrief, MovieListResponse, GenreOut
from app.services.tmdb_service import tmdb_service

router = APIRouter(prefix="/api/movies", tags=["movies"])


def _build_movie_out(movie: Movie) -> MovieOut:
    """Build MovieOut — watch_providers JSON string is parsed by field_validator."""
    return MovieOut.model_validate(movie)


def _fetch_tmdb_and_update(movie_id: int) -> None:
    """Background task: fetch TMDB data for a movie and persist it."""
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        movie = db.query(Movie).filter(Movie.id == movie_id).first()
        if not movie:
            return
        settings = get_settings()
        if not settings.tmdb_api_key:
            return
        details = tmdb_service.get_movie_details(movie.tmdb_id)
        if details:
            movie.poster_path = details.get("poster_path", "") or movie.poster_path
            movie.backdrop_path = details.get("backdrop_path", "") or movie.backdrop_path
        providers = tmdb_service.get_watch_providers(movie.tmdb_id)
        movie.watch_providers = json.dumps(providers)
        movie.trailer_url = tmdb_service.get_movie_videos(movie.tmdb_id)
        db.commit()
    except Exception:
        pass
    finally:
        db.close()


@router.get("", response_model=MovieListResponse)
def list_movies(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    genre: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = Query("popularity", pattern="^(popularity|vote_average|release_date|title)$"),
    content_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Movie).options(joinedload(Movie.genres))

    if genre:
        query = query.join(Movie.genres).filter(Genre.name.ilike(genre))

    if search:
        query = query.filter(
            or_(
                Movie.title.ilike(f"%{search}%"),
                Movie.overview.ilike(f"%{search}%"),
                Movie.director.ilike(f"%{search}%"),
            )
        )

    if content_type:
        query = query.filter(Movie.content_type == content_type)

    total = query.count()

    sort_column = getattr(Movie, sort_by)
    if sort_by in ("popularity", "vote_average"):
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column)

    movies = query.offset((page - 1) * per_page).limit(per_page).all()

    return MovieListResponse(
        movies=[MovieBrief.model_validate(m) for m in movies],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/genres", response_model=list[GenreOut])
def list_genres(db: Session = Depends(get_db)):
    return db.query(Genre).order_by(Genre.name).all()


@router.get("/trending", response_model=list[MovieBrief])
def trending_movies(limit: int = Query(20, ge=1, le=50), db: Session = Depends(get_db)):
    movies = (
        db.query(Movie)
        .options(joinedload(Movie.genres))
        .order_by(Movie.popularity.desc())
        .limit(limit)
        .all()
    )
    return [MovieBrief.model_validate(m) for m in movies]


@router.get("/by-genre", response_model=dict[str, list[MovieBrief]])
def movies_by_genre(
    limit: int = Query(15, ge=1, le=30),
    db: Session = Depends(get_db),
):
    """Get top movies grouped by genre (for Netflix-style rows)."""
    genres = db.query(Genre).order_by(Genre.name).all()
    result = {}
    for genre in genres:
        movies = (
            db.query(Movie)
            .options(joinedload(Movie.genres))
            .join(Movie.genres)
            .filter(Genre.id == genre.id)
            .order_by(Movie.popularity.desc())
            .limit(limit)
            .all()
        )
        if movies:
            result[genre.name] = [MovieBrief.model_validate(m) for m in movies]
    return result


@router.get("/featured", response_model=list[MovieOut])
def featured_movies(db: Session = Depends(get_db)):
    """Get top 5 movies for hero banner."""
    movies = (
        db.query(Movie)
        .options(joinedload(Movie.genres))
        .filter(Movie.vote_average >= 7.0)
        .order_by(Movie.popularity.desc())
        .limit(5)
        .all()
    )
    return [_build_movie_out(m) for m in movies]


@router.get("/{movie_id}/watch")
def get_watch_link(movie_id: int, db: Session = Depends(get_db)):
    """Get direct watch link for a movie (JustWatch fallback)."""
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    try:
        providers = json.loads(movie.watch_providers or "[]")
    except Exception:
        providers = []

    justwatch_url = (
        f"https://www.justwatch.com/us/search?q={movie.title.replace(' ', '+')}"
    )

    return {
        "title": movie.title,
        "providers": providers,
        "justwatch_url": justwatch_url,
        "tmdb_url": f"https://www.themoviedb.org/movie/{movie.tmdb_id}/watch",
    }


@router.get("/{movie_id}", response_model=MovieOut)
def get_movie(
    movie_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    movie = (
        db.query(Movie)
        .options(joinedload(Movie.genres))
        .filter(Movie.id == movie_id)
        .first()
    )
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    # If poster is missing and TMDB key is set, fetch in background
    settings = get_settings()
    if movie.poster_path == "" and settings.tmdb_api_key:
        background_tasks.add_task(_fetch_tmdb_and_update, movie_id)

    return _build_movie_out(movie)
