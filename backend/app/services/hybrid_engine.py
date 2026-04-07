from sqlalchemy.orm import Session, joinedload

from app.config import get_settings
from app.models.movie import Movie
from app.models.rating import Rating
from app.schemas.movie import MovieBrief
from app.schemas.recommendation import RecommendationItem, RecommendationResponse
from app.services.content_based import ContentBasedEngine
from app.services.collaborative import CollaborativeEngine

settings = get_settings()


class HybridEngine:
    def __init__(self):
        self.content_engine = ContentBasedEngine()
        self.collab_engine = CollaborativeEngine()
        self.movie_popularity: dict[int, float] = {}  # movie_id -> normalized popularity

    def load_models(self, content_path: str, collab_path: str):
        self.content_engine.load(content_path)
        self.collab_engine.load(collab_path)

    def set_popularity(self, popularity_map: dict[int, float]):
        """Set pre-computed normalized popularity scores."""
        self.movie_popularity = popularity_map

    def recommend(
        self, user_id: int, db: Session, top_n: int = 20
    ) -> RecommendationResponse:
        # Get user's ratings
        user_ratings = db.query(Rating).filter(Rating.user_id == user_id).all()
        rated_ids = {r.movie_id for r in user_ratings}
        liked_ids = [r.movie_id for r in user_ratings if r.score >= 3.5]

        use_collaborative = (
            self.collab_engine.is_trained and len(user_ratings) >= settings.cold_start_threshold
        )

        if not liked_ids:
            # No ratings at all -> return popular movies
            return self._popular_recommendations(db, top_n, rated_ids)

        # Content-based scores
        content_recs = self.content_engine.get_user_recommendations(
            liked_ids, top_n=100, exclude_ids=rated_ids
        )
        content_scores = {mid: score for mid, score in content_recs}

        # Collaborative scores
        collab_scores: dict[int, float] = {}
        if use_collaborative:
            collab_recs = self.collab_engine.get_user_recommendations(
                user_id, rated_ids, top_n=100
            )
            # Normalize to 0-1 range
            if collab_recs:
                max_score = max(s for _, s in collab_recs)
                min_score = min(s for _, s in collab_recs)
                spread = max_score - min_score if max_score != min_score else 1.0
                collab_scores = {mid: (s - min_score) / spread for mid, s in collab_recs}

        # Combine all candidate movie ids
        all_candidates = set(content_scores.keys()) | set(collab_scores.keys())

        # Compute hybrid scores
        scored: list[tuple[int, float]] = []
        for mid in all_candidates:
            c_score = content_scores.get(mid, 0.0)
            co_score = collab_scores.get(mid, 0.0)
            p_score = self.movie_popularity.get(mid, 0.0)

            if use_collaborative:
                final = (
                    settings.content_weight * c_score
                    + settings.collaborative_weight * co_score
                    + settings.popularity_weight * p_score
                )
            else:
                # Cold start: heavier on content + popularity
                final = 0.7 * c_score + 0.3 * p_score

            scored.append((mid, final))

        scored.sort(key=lambda x: x[1], reverse=True)
        top_ids = [mid for mid, _ in scored[:top_n]]

        # Fetch movie objects
        movies_map = self._fetch_movies(db, top_ids)

        # Build response with reasons
        strategy = "hybrid" if use_collaborative else "content_based"
        items = []
        for mid, score in scored[:top_n]:
            if mid not in movies_map:
                continue
            movie = movies_map[mid]
            reason = self._generate_reason(mid, liked_ids, content_scores, use_collaborative)
            items.append(
                RecommendationItem(
                    movie=MovieBrief.model_validate(movie),
                    score=round(score, 4),
                    reason=reason,
                )
            )

        return RecommendationResponse(recommendations=items, strategy=strategy)

    def get_similar_movies(
        self, movie_id: int, db: Session, top_n: int = 10
    ) -> list[RecommendationItem]:
        similar = self.content_engine.get_similar(movie_id, top_n=top_n)
        if not similar:
            return []

        movie_ids = [mid for mid, _ in similar]
        movies_map = self._fetch_movies(db, movie_ids)

        source_movie = db.query(Movie).filter(Movie.id == movie_id).first()
        source_title = source_movie.title if source_movie else "this movie"

        items = []
        for mid, score in similar:
            if mid in movies_map:
                items.append(
                    RecommendationItem(
                        movie=MovieBrief.model_validate(movies_map[mid]),
                        score=round(score, 4),
                        reason=f"Similar to {source_title}",
                    )
                )
        return items

    def _popular_recommendations(
        self, db: Session, top_n: int, exclude_ids: set[int]
    ) -> RecommendationResponse:
        query = db.query(Movie).options(joinedload(Movie.genres))
        if exclude_ids:
            query = query.filter(~Movie.id.in_(exclude_ids))
        movies = query.order_by(Movie.popularity.desc()).limit(top_n).all()

        items = [
            RecommendationItem(
                movie=MovieBrief.model_validate(m),
                score=round(m.popularity / 100, 4),
                reason="Trending now",
            )
            for m in movies
        ]
        return RecommendationResponse(recommendations=items, strategy="popular")

    def _fetch_movies(self, db: Session, movie_ids: list[int]) -> dict[int, Movie]:
        if not movie_ids:
            return {}
        movies = (
            db.query(Movie)
            .options(joinedload(Movie.genres))
            .filter(Movie.id.in_(movie_ids))
            .all()
        )
        return {m.id: m for m in movies}

    def _generate_reason(
        self,
        movie_id: int,
        liked_ids: list[int],
        content_scores: dict[int, float],
        use_collaborative: bool,
    ) -> str:
        if movie_id in content_scores and content_scores[movie_id] > 0.3:
            return "Matches your taste in movies"
        if use_collaborative:
            return "Users with similar taste enjoyed this"
        return "Popular and highly rated"


# Global instance
hybrid_engine = HybridEngine()
