from pydantic import BaseModel


class GenreOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


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

    model_config = {"from_attributes": True}


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
