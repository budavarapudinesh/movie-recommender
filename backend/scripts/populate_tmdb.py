"""Populate poster images and watch providers from TMDB API.

Usage:
    TMDB_API_KEY=your_key python scripts/populate_tmdb.py
    Or set TMDB_API_KEY in backend/.env first.
    Get a free key at: https://www.themoviedb.org/settings/api
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import SessionLocal
from app.models.movie import Movie
from app.services.tmdb_service import tmdb_service


def populate(limit: int = None, skip_existing: bool = True):
    if not tmdb_service._has_key():
        print("ERROR: TMDB_API_KEY not set in .env")
        print("Get a free key at: https://www.themoviedb.org/settings/api")
        sys.exit(1)

    db = SessionLocal()
    try:
        query = db.query(Movie)
        if skip_existing:
            query = query.filter(Movie.poster_path == "")
        movies = query.all()
        if limit:
            movies = movies[:limit]

        print(f"Populating {len(movies)} movies...")
        for i, movie in enumerate(movies):
            details = tmdb_service.get_movie_details(movie.tmdb_id)
            if details:
                movie.poster_path = details.get("poster_path", "") or ""
                movie.backdrop_path = details.get("backdrop_path", "") or ""

            providers = tmdb_service.get_watch_providers(movie.tmdb_id)
            movie.watch_providers = json.dumps(providers)

            trailer = tmdb_service.get_movie_videos(movie.tmdb_id)
            movie.trailer_url = trailer

            # Detect anime: Animation genre + Japanese original language
            genres = [g.name for g in movie.genres]
            if "Animation" in genres and movie.original_language == "ja":
                movie.content_type = "anime"
            else:
                movie.content_type = "movie"

            if (i + 1) % 50 == 0:
                db.commit()
                print(f"  Progress: {i + 1}/{len(movies)}")
                time.sleep(0.25)  # respect TMDB rate limits

        db.commit()
        print(f"Done! Populated {len(movies)} movies.")
    finally:
        db.close()


if __name__ == "__main__":
    populate()
