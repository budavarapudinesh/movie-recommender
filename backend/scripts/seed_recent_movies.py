"""
Seed recent popular movies (2018-2024) from TMDB into the local SQLite database.

Usage:
    cd backend
    source venv/bin/activate
    TMDB_API_KEY=your_key python scripts/seed_recent_movies.py
    OR set TMDB_API_KEY in backend/.env first.
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx
from app.database import SessionLocal, Base, engine
from app.models.movie import Movie, Genre

TMDB_BASE = "https://api.themoviedb.org/3"

# Load API key from env
from app.config import get_settings
settings = get_settings()
TMDB_API_KEY = settings.tmdb_api_key


def fetch_popular_recent(year: int, page: int) -> list[dict]:
    """Fetch popular movies for a given year from TMDB discover endpoint."""
    try:
        with httpx.Client(timeout=15) as client:
            r = client.get(
                f"{TMDB_BASE}/discover/movie",
                params={
                    "api_key": TMDB_API_KEY,
                    "sort_by": "popularity.desc",
                    "primary_release_year": year,
                    "page": page,
                    "vote_count.gte": 100,
                    "language": "en-US",
                },
            )
            r.raise_for_status()
            return r.json().get("results", [])
    except Exception as e:
        print(f"  TMDB error for year {year} page {page}: {e}")
        return []


def fetch_movie_details(tmdb_id: int) -> dict:
    """Fetch full details for a movie including genres, runtime, etc."""
    try:
        with httpx.Client(timeout=15) as client:
            r = client.get(
                f"{TMDB_BASE}/movie/{tmdb_id}",
                params={"api_key": TMDB_API_KEY, "append_to_response": "credits"},
            )
            r.raise_for_status()
            return r.json()
    except Exception as e:
        print(f"  TMDB details error for {tmdb_id}: {e}")
        return {}


def get_or_create_genre(db, name: str, genre_cache: dict) -> Genre:
    if name in genre_cache:
        return genre_cache[name]
    genre = db.query(Genre).filter(Genre.name == name).first()
    if not genre:
        genre = Genre(name=name)
        db.add(genre)
        db.flush()
    genre_cache[name] = genre
    return genre


def seed(years: range = range(2018, 2025), pages_per_year: int = 5):
    if not TMDB_API_KEY:
        print("ERROR: TMDB_API_KEY not set in backend/.env")
        print("Get a free key at: https://www.themoviedb.org/settings/api")
        sys.exit(1)

    print(f"Seeding recent movies from TMDB ({years.start}-{years.stop - 1})...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    genre_cache: dict[str, Genre] = {}
    added = 0
    skipped = 0

    try:
        for year in years:
            print(f"\n📅 Year: {year}")
            for page in range(1, pages_per_year + 1):
                results = fetch_popular_recent(year, page)
                if not results:
                    break

                for item in results:
                    tmdb_id = item.get("id")
                    if not tmdb_id:
                        continue

                    # Skip if already exists
                    existing = db.query(Movie).filter(Movie.tmdb_id == tmdb_id).first()
                    if existing:
                        skipped += 1
                        continue

                    # Fetch full details
                    details = fetch_movie_details(tmdb_id)
                    if not details:
                        continue

                    # Build genres
                    movie_genre_objs = []
                    for g in details.get("genres", []):
                        gobj = get_or_create_genre(db, g["name"], genre_cache)
                        movie_genre_objs.append(gobj)

                    # Director from credits
                    director = ""
                    top_cast = ""
                    credits = details.get("credits", {})
                    for member in credits.get("crew", []):
                        if member.get("job") == "Director":
                            director = member.get("name", "")
                            break
                    top_cast = ",".join(
                        c["name"] for c in credits.get("cast", [])[:5]
                    )

                    # Detect anime
                    genre_names = [g["name"] for g in details.get("genres", [])]
                    is_anime = (
                        "Animation" in genre_names
                        and details.get("original_language") == "ja"
                    )

                    movie = Movie(
                        tmdb_id=tmdb_id,
                        title=details.get("title") or item.get("title", "Unknown"),
                        overview=details.get("overview", ""),
                        release_date=details.get("release_date", ""),
                        runtime=details.get("runtime") or 0,
                        vote_average=details.get("vote_average", 0.0),
                        vote_count=details.get("vote_count", 0),
                        popularity=details.get("popularity", 0.0),
                        poster_path=details.get("poster_path") or "",
                        backdrop_path=details.get("backdrop_path") or "",
                        original_language=details.get("original_language", "en"),
                        budget=details.get("budget") or 0,
                        revenue=details.get("revenue") or 0,
                        tagline=details.get("tagline") or "",
                        director=director,
                        top_cast=top_cast,
                        watch_providers="[]",
                        trailer_url="",
                        content_type="anime" if is_anime else "movie",
                    )
                    movie.genres = movie_genre_objs
                    db.add(movie)
                    added += 1

                    if added % 50 == 0:
                        db.commit()
                        print(f"  ✅ {added} movies added so far...")

                    time.sleep(0.05)  # polite rate limit

                db.commit()
                time.sleep(0.3)

        db.commit()
        print(f"\n🎬 Done! Added {added} new movies, skipped {skipped} existing.")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
