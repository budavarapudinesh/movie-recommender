from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from app.database import get_db
from app.models.movie import Movie, Genre
from app.schemas.movie import MovieOut, MovieBrief, MovieListResponse, GenreOut

router = APIRouter(prefix="/api/movies", tags=["movies"])


@router.get("", response_model=MovieListResponse)
def list_movies(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    genre: str | None = None,
    search: str | None = None,
    sort_by: str = Query("popularity", pattern="^(popularity|vote_average|release_date|title)$"),
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
    return movies


@router.get("/{movie_id}", response_model=MovieOut)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(Movie).options(joinedload(Movie.genres)).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie
