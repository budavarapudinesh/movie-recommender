"""Generate synthetic user ratings for cold-start testing."""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import SessionLocal
from app.models.movie import Movie
from app.models.user import User
from app.models.rating import Rating
from app.services.auth_service import hash_password

NUM_USERS = 50
RATINGS_PER_USER = (10, 40)  # min, max ratings per user


def seed():
    db = SessionLocal()
    try:
        movie_ids = [m.id for m in db.query(Movie.id).all()]
        if not movie_ids:
            print("No movies in database. Run load_dataset.py first.")
            return

        print(f"Found {len(movie_ids)} movies. Creating {NUM_USERS} synthetic users...")

        users = []
        for i in range(1, NUM_USERS + 1):
            user = User(
                username=f"user{i}",
                email=f"user{i}@example.com",
                hashed_password=hash_password("password123"),
            )
            db.add(user)
            users.append(user)

        db.flush()

        total_ratings = 0
        for user in users:
            n_ratings = random.randint(*RATINGS_PER_USER)
            sampled = random.sample(movie_ids, min(n_ratings, len(movie_ids)))

            for mid in sampled:
                # Weighted distribution: more 3-4 star ratings (realistic)
                score = random.choice(
                    [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.0, 3.5, 3.5, 3.5, 4.0, 4.0, 4.5, 5.0]
                )
                db.add(Rating(user_id=user.id, movie_id=mid, score=score))
                total_ratings += 1

        db.commit()
        print(f"Created {NUM_USERS} users with {total_ratings} total ratings.")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
