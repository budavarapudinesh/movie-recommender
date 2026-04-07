"""Training pipeline for recommendation models."""
import sys
from pathlib import Path

# Add backend to path when running as script
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.movie import Movie
from app.models.user import User  # noqa: F401 - needed for SQLAlchemy relationship resolution
from app.models.rating import Rating
from app.services.content_based import ContentBasedEngine
from app.services.collaborative import CollaborativeEngine

MODEL_DIR = Path(__file__).parent / "model_store"
CONTENT_MODEL_PATH = str(MODEL_DIR / "content_based.pkl")
COLLAB_MODEL_PATH = str(MODEL_DIR / "collaborative.pkl")


def train_content_based(db: Session) -> ContentBasedEngine:
    print("Training content-based model...")
    movies = db.query(Movie).all()

    movie_data = []
    for m in movies:
        genres_str = " ".join(g.name for g in m.genres)
        cast_str = m.top_cast.replace(",", " ") if m.top_cast else ""
        features = f"{m.overview or ''} {genres_str} {cast_str} {m.director or ''}"
        movie_data.append({"id": m.id, "features": features})

    engine = ContentBasedEngine()
    engine.fit(movie_data)
    engine.save(CONTENT_MODEL_PATH)
    print(f"Content-based model trained on {len(movie_data)} movies. Saved to {CONTENT_MODEL_PATH}")
    return engine


def train_collaborative(db: Session) -> CollaborativeEngine:
    print("Training collaborative filtering model...")
    ratings = db.query(Rating).all()

    if len(ratings) < 10:
        print("Not enough ratings for collaborative filtering. Skipping.")
        engine = CollaborativeEngine()
        engine.save(COLLAB_MODEL_PATH)
        return engine

    ratings_data = [{"user_id": r.user_id, "movie_id": r.movie_id, "score": r.score} for r in ratings]

    engine = CollaborativeEngine()
    engine.fit(ratings_data)
    engine.save(COLLAB_MODEL_PATH)
    print(f"Collaborative model trained on {len(ratings_data)} ratings. Saved to {COLLAB_MODEL_PATH}")
    return engine


def get_popularity_map(db: Session) -> dict[int, float]:
    movies = db.query(Movie.id, Movie.popularity).all()
    if not movies:
        return {}
    max_pop = max(m.popularity for m in movies) or 1.0
    return {m.id: m.popularity / max_pop for m in movies}


def train_all():
    db = SessionLocal()
    try:
        train_content_based(db)
        train_collaborative(db)
        print("All models trained successfully!")
    finally:
        db.close()


if __name__ == "__main__":
    train_all()
