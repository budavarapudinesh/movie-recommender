from sqlalchemy import Column, Integer, String, Float, Text, Table, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base

movie_genres = Table(
    "movie_genres",
    Base.metadata,
    Column("movie_id", Integer, ForeignKey("movies.id"), primary_key=True),
    Column("genre_id", Integer, ForeignKey("genres.id"), primary_key=True),
)


class Genre(Base):
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

    movies = relationship("Movie", secondary=movie_genres, back_populates="genres")


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    tmdb_id = Column(Integer, unique=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    overview = Column(Text, default="")
    release_date = Column(String(20), default="")
    runtime = Column(Integer, default=0)
    vote_average = Column(Float, default=0.0)
    vote_count = Column(Integer, default=0)
    popularity = Column(Float, default=0.0)
    poster_path = Column(String(255), default="")
    backdrop_path = Column(String(255), default="")
    original_language = Column(String(10), default="en")
    budget = Column(Integer, default=0)
    revenue = Column(Integer, default=0)
    tagline = Column(String(500), default="")
    director = Column(String(255), default="")
    top_cast = Column(Text, default="")  # comma-separated top 5 cast names
    watch_providers = Column(Text, default="[]")   # JSON string of provider list
    content_type = Column(String(20), default="movie")  # "movie", "tv", "anime"
    trailer_url = Column(String(500), default="")

    genres = relationship("Genre", secondary=movie_genres, back_populates="movies")
    ratings = relationship("Rating", back_populates="movie")
