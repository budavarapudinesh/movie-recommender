import pickle
from pathlib import Path

from surprise import SVD, Dataset, Reader
import pandas as pd


class CollaborativeEngine:
    def __init__(self):
        self.model = SVD(n_factors=100, n_epochs=20, lr_all=0.005, reg_all=0.02)
        self.is_trained = False
        self.all_movie_ids: set[int] = set()

    def fit(self, ratings_data: list[dict]):
        """
        ratings_data: list of {"user_id": int, "movie_id": int, "score": float}
        """
        if len(ratings_data) < 10:
            return

        df = pd.DataFrame(ratings_data)
        self.all_movie_ids = set(df["movie_id"].unique())

        reader = Reader(rating_scale=(0.5, 5.0))
        dataset = Dataset.load_from_df(df[["user_id", "movie_id", "score"]], reader)
        trainset = dataset.build_full_trainset()
        self.model.fit(trainset)
        self.is_trained = True

    def predict(self, user_id: int, movie_id: int) -> float:
        """Predict rating for a user-movie pair."""
        if not self.is_trained:
            return 0.0
        return self.model.predict(user_id, movie_id).est

    def get_user_recommendations(
        self, user_id: int, rated_movie_ids: set[int], candidate_ids: list[int] | None = None, top_n: int = 20
    ) -> list[tuple[int, float]]:
        """Predict ratings for all unrated movies, return top-N."""
        if not self.is_trained:
            return []

        candidates = candidate_ids if candidate_ids else list(self.all_movie_ids)
        predictions = []
        for mid in candidates:
            if mid not in rated_movie_ids:
                pred = self.model.predict(user_id, mid)
                predictions.append((mid, pred.est))

        predictions.sort(key=lambda x: x[1], reverse=True)
        return predictions[:top_n]

    def save(self, path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(
                {"model": self.model, "is_trained": self.is_trained, "all_movie_ids": self.all_movie_ids},
                f,
            )

    def load(self, path: str) -> bool:
        if not Path(path).exists():
            return False
        with open(path, "rb") as f:
            data = pickle.load(f)
        self.model = data["model"]
        self.is_trained = data["is_trained"]
        self.all_movie_ids = data["all_movie_ids"]
        return True
