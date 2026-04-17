import json
from typing import Any

from pydantic import BaseModel, field_validator


class GenreOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class WatchProvider(BaseModel):
    provider_id: int
    provider_name: str
    logo_path: str
    type: str
    link: str


class MovieOut(BaseModel):
    id: int
    tmdb_id: int
    title: str
    overview: str
    release_date: str
    runtime: int
    vote_average: float
    vote_count: int
    popularity: float
    poster_path: str
    backdrop_path: str
    original_language: str
    tagline: str
    director: str
    top_cast: str
    genres: list[GenreOut]
    watch_providers: list[WatchProvider] = []
    content_type: str = "movie"
    trailer_url: str = ""

    model_config = {"from_attributes": True}

    @field_validator("watch_providers", mode="before")
    @classmethod
    def parse_watch_providers(cls, v: Any) -> Any:
        """Accept either a JSON string (from ORM) or a list (already parsed)."""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return []
        return v if v is not None else []


class MovieBrief(BaseModel):
    id: int
    tmdb_id: int
    title: str
    vote_average: float
    poster_path: str
    release_date: str
    genres: list[GenreOut]

    model_config = {"from_attributes": True}


class MovieListResponse(BaseModel):
    movies: list[MovieBrief]
    total: int
    page: int
    per_page: int
