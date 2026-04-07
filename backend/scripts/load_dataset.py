"""Load TMDB 5000 dataset into SQLite database."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
from app.database import engine, SessionLocal, Base
from app.models.movie import Movie, Genre, movie_genres
from app.models.user import User
from app.models.rating import Rating

DATA_DIR = Path(__file__).parent.parent / "data"


def load_tmdb_data():
    movies_csv = DATA_DIR / "tmdb_5000_movies.csv"
    credits_csv = DATA_DIR / "tmdb_5000_credits.csv"

    if not movies_csv.exists() or not credits_csv.exists():
        print(f"ERROR: Dataset files not found in {DATA_DIR}/")
        print("Please download the TMDB 5000 Movie Dataset:")
        print("  1. Go to https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata")
        print(f"  2. Place tmdb_5000_movies.csv and tmdb_5000_credits.csv in {DATA_DIR}/")
        sys.exit(1)

    print("Reading CSV files...")
    movies_df = pd.read_csv(movies_csv)
    credits_df = pd.read_csv(credits_csv)

    # Merge on movie_id/id
    if "movie_id" in credits_df.columns:
        credits_df = credits_df.rename(columns={"movie_id": "id"})
    merged = movies_df.merge(credits_df, on="id", how="left", suffixes=("", "_credits"))

    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Collect all unique genres
        all_genres: set[str] = set()
        for genres_json in movies_df["genres"].dropna():
            try:
                for g in json.loads(genres_json):
                    all_genres.add(g["name"])
            except (json.JSONDecodeError, KeyError):
                pass

        # Insert genres
        genre_map: dict[str, Genre] = {}
        for name in sorted(all_genres):
            genre = Genre(name=name)
            db.add(genre)
            db.flush()
            genre_map[name] = genre

        print(f"Inserted {len(genre_map)} genres.")

        # Insert movies
        count = 0
        for _, row in merged.iterrows():
            # Parse genres
            movie_genres_list = []
            try:
                for g in json.loads(row.get("genres", "[]") or "[]"):
                    if g["name"] in genre_map:
                        movie_genres_list.append(genre_map[g["name"]])
            except (json.JSONDecodeError, KeyError, TypeError):
                pass

            # Parse director from crew
            director = ""
            try:
                crew = json.loads(row.get("crew", "[]") or "[]")
                for member in crew:
                    if member.get("job") == "Director":
                        director = member.get("name", "")
                        break
            except (json.JSONDecodeError, KeyError, TypeError):
                pass

            # Parse top cast
            top_cast = ""
            try:
                cast = json.loads(row.get("cast", "[]") or "[]")
                top_cast = ",".join(c["name"] for c in cast[:5])
            except (json.JSONDecodeError, KeyError, TypeError):
                pass

            def safe_int(val, default=0):
                try:
                    import math
                    if val is None or (isinstance(val, float) and math.isnan(val)):
                        return default
                    return int(val)
                except (ValueError, TypeError):
                    return default

            def safe_float(val, default=0.0):
                try:
                    import math
                    if val is None or (isinstance(val, float) and math.isnan(val)):
                        return default
                    return float(val)
                except (ValueError, TypeError):
                    return default

            def safe_str(val, default=""):
                if val is None or (isinstance(val, float) and str(val) == "nan"):
                    return default
                return str(val)

            movie = Movie(
                tmdb_id=safe_int(row["id"]),
                title=safe_str(row.get("title", row.get("original_title", "Unknown")), "Unknown"),
                overview=safe_str(row.get("overview", "")),
                release_date=safe_str(row.get("release_date", "")),
                runtime=safe_int(row.get("runtime", 0)),
                vote_average=safe_float(row.get("vote_average", 0)),
                vote_count=safe_int(row.get("vote_count", 0)),
                popularity=safe_float(row.get("popularity", 0)),
                poster_path=safe_str(row.get("poster_path", "")),
                backdrop_path=safe_str(row.get("backdrop_path", "")),
                original_language=safe_str(row.get("original_language", "en"), "en"),
                budget=safe_int(row.get("budget", 0)),
                revenue=safe_int(row.get("revenue", 0)),
                tagline=safe_str(row.get("tagline", "")),
                director=director,
                top_cast=top_cast,
            )
            movie.genres = movie_genres_list
            db.add(movie)
            count += 1

            if count % 500 == 0:
                print(f"  Loaded {count} movies...")
                db.flush()

        db.commit()
        print(f"Successfully loaded {count} movies into the database!")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    load_tmdb_data()
