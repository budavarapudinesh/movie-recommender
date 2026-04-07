import pickle
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class ContentBasedEngine:
    def __init__(self):
        self.tfidf_matrix = None
        self.movie_ids: list[int] = []
        self.id_to_idx: dict[int, int] = {}
        self.vectorizer = TfidfVectorizer(stop_words="english", max_features=10000)

    def fit(self, movie_data: list[dict]):
        """
        movie_data: list of {"id": int, "features": str}
        where features = "overview genres cast director"
        """
        self.movie_ids = [m["id"] for m in movie_data]
        self.id_to_idx = {mid: idx for idx, mid in enumerate(self.movie_ids)}

        corpus = [m["features"] for m in movie_data]
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    def get_similar(self, movie_id: int, top_n: int = 20) -> list[tuple[int, float]]:
        """Returns list of (movie_id, similarity_score) sorted by score desc."""
        if movie_id not in self.id_to_idx:
            return []

        idx = self.id_to_idx[movie_id]
        movie_vec = self.tfidf_matrix[idx : idx + 1]
        scores = cosine_similarity(movie_vec, self.tfidf_matrix).flatten()
        scores[idx] = -1  # exclude self

        top_indices = np.argsort(scores)[::-1][:top_n]
        return [(self.movie_ids[i], float(scores[i])) for i in top_indices]

    def get_user_recommendations(
        self, liked_movie_ids: list[int], top_n: int = 20, exclude_ids: set[int] | None = None
    ) -> list[tuple[int, float]]:
        """Recommend based on average similarity to liked movies."""
        if not liked_movie_ids or self.tfidf_matrix is None:
            return []

        exclude = exclude_ids or set()
        liked_indices = [self.id_to_idx[mid] for mid in liked_movie_ids if mid in self.id_to_idx]
        if not liked_indices:
            return []

        liked_vecs = self.tfidf_matrix[liked_indices]
        avg_vec = liked_vecs.mean(axis=0)
        scores = cosine_similarity(avg_vec, self.tfidf_matrix).flatten()

        # Zero out liked and excluded movies
        for mid in liked_movie_ids:
            if mid in self.id_to_idx:
                scores[self.id_to_idx[mid]] = -1
        for mid in exclude:
            if mid in self.id_to_idx:
                scores[self.id_to_idx[mid]] = -1

        top_indices = np.argsort(scores)[::-1][:top_n]
        return [(self.movie_ids[i], float(scores[i])) for i in top_indices if scores[i] > 0]

    def save(self, path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(
                {
                    "tfidf_matrix": self.tfidf_matrix,
                    "movie_ids": self.movie_ids,
                    "id_to_idx": self.id_to_idx,
                    "vectorizer": self.vectorizer,
                },
                f,
            )

    def load(self, path: str) -> bool:
        if not Path(path).exists():
            return False
        with open(path, "rb") as f:
            data = pickle.load(f)
        self.tfidf_matrix = data["tfidf_matrix"]
        self.movie_ids = data["movie_ids"]
        self.id_to_idx = data["id_to_idx"]
        self.vectorizer = data["vectorizer"]
        return True
