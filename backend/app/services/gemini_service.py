import logging
import time

from google import genai
from google.genai import types
from sqlalchemy.orm import Session, joinedload

logger = logging.getLogger(__name__)

from app.config import get_settings
from app.models.movie import Movie
from app.models.rating import Rating
from app.schemas.movie import MovieBrief

settings = get_settings()

# Circuit breaker constants
_CB_FAILURE_THRESHOLD = 3   # consecutive failures to trip
_CB_RECOVERY_TIMEOUT = 60   # seconds before retrying after trip
_REQUEST_TIMEOUT = 15       # seconds per Gemini API call

SYSTEM_PROMPT = """You are a movie recommendation assistant. You help users discover movies they'll love.

You have access to a database of movies. When recommending movies, always:
1. Consider the user's preferences and rating history
2. Explain WHY you're recommending each movie
3. Be conversational and enthusiastic about films
4. If the user asks for something specific (genre, mood, similar to X), focus on that
5. Provide 3-5 recommendations per response
6. Include the movie title, year, and a brief reason for each recommendation

Format movie recommendations as:
**Movie Title (Year)** - Brief reason why they'd enjoy it

{user_context}"""


class GeminiService:
    def __init__(self):
        self._client = None
        # Circuit breaker state
        self._consecutive_failures = 0
        self._last_failure_time: float = 0

    @property
    def client(self):
        if self._client is None and settings.gemini_api_key:
            self._client = genai.Client(api_key=settings.gemini_api_key)
        return self._client

    def _is_circuit_open(self) -> bool:
        """Check if circuit breaker is tripped (too many recent failures)."""
        if self._consecutive_failures < _CB_FAILURE_THRESHOLD:
            return False
        elapsed = time.monotonic() - self._last_failure_time
        if elapsed > _CB_RECOVERY_TIMEOUT:
            # Recovery window passed — allow a retry
            logger.info("Circuit breaker recovery: allowing retry after %.0fs", elapsed)
            return False
        return True

    def _record_success(self):
        self._consecutive_failures = 0

    def _record_failure(self):
        self._consecutive_failures += 1
        self._last_failure_time = time.monotonic()

    def chat(
        self,
        message: str,
        history: list[dict],
        user_id: int | None,
        db: Session | None,
    ) -> tuple[str, list[int]]:
        """
        Chat with Gemini for movie recommendations.
        Returns (reply_text, list_of_recommended_movie_ids).
        """
        if not self.client:
            return "Gemini API key not configured. Please set GEMINI_API_KEY.", []

        if self._is_circuit_open():
            logger.warning("Circuit breaker OPEN: skipping Gemini API call")
            return "The AI assistant is temporarily unavailable. Please try again later.", []

        # Build user context from their ratings
        user_context = ""
        if user_id and db:
            user_context = self._build_user_context(user_id, db)

        system = SYSTEM_PROMPT.format(user_context=user_context)

        # Build conversation contents
        contents = []
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])]))
        contents.append(types.Content(role="user", parts=[types.Part.from_text(text=message)]))

        try:
            from google.genai.types import HttpOptions
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system,
                    temperature=0.8,
                    max_output_tokens=1024,
                    http_options=HttpOptions(timeout=_REQUEST_TIMEOUT)
                ),
            )
            self._record_success()
            reply = response.text or "I couldn't generate a response. Please try again."
        except Exception as e:
            self._record_failure()
            logger.error(f"Gemini API error: {e}")
            return "The AI assistant is temporarily unavailable. Please try again later.", []

        # Try to match mentioned movies from DB
        mentioned_ids = self._extract_movie_ids(reply, db) if db else []

        return reply, mentioned_ids

    def _build_user_context(self, user_id: int, db: Session) -> str:
        ratings = (
            db.query(Rating)
            .options(joinedload(Rating.movie).joinedload(Movie.genres))
            .filter(Rating.user_id == user_id)
            .order_by(Rating.score.desc())
            .limit(20)
            .all()
        )

        if not ratings:
            return "The user hasn't rated any movies yet."

        liked = [r for r in ratings if r.score >= 4.0]
        disliked = [r for r in ratings if r.score <= 2.0]

        lines = ["User's movie preferences:"]
        if liked:
            liked_str = ", ".join(f"{r.movie.title} ({r.score}/5)" for r in liked[:10])
            lines.append(f"Loved: {liked_str}")
        if disliked:
            disliked_str = ", ".join(f"{r.movie.title} ({r.score}/5)" for r in disliked[:5])
            lines.append(f"Disliked: {disliked_str}")

        # Genre preferences
        genre_counts: dict[str, int] = {}
        for r in ratings:
            if r.score >= 3.5:
                for g in r.movie.genres:
                    genre_counts[g.name] = genre_counts.get(g.name, 0) + 1
        if genre_counts:
            top_genres = sorted(genre_counts, key=genre_counts.get, reverse=True)[:5]
            lines.append(f"Favorite genres: {', '.join(top_genres)}")

        return "\n".join(lines)

    def _extract_movie_ids(self, text: str, db: Session) -> list[int]:
        """Try to find mentioned movie titles in the database."""
        # Use popular movies only for matching (performance optimization)
        movies = (
            db.query(Movie.id, Movie.title)
            .order_by(Movie.popularity.desc())
            .limit(500)
            .all()
        )
        found = []
        text_lower = text.lower()
        for mid, title in movies:
            if title.lower() in text_lower and len(title) > 3:
                found.append(mid)
        return found[:10]

    def is_entertainment_query(self, query: str) -> bool:
        """
        Check if the query is related to movies, tv series, actors, or entertainment.
        Defaults to True (allow) when uncertain — only rejects obvious non-entertainment queries.
        """
        if not self.client or self._is_circuit_open():
            if not self.client:
                logger.warning("Gemini API key missing. Defaulting to True for query classification.")
            else:
                logger.warning("Circuit breaker OPEN: defaulting to True for classification")
            return True

        system = (
            "You are a strict entertainment search guard for a movie/TV streaming platform. "
            "A user has typed a search query. Respond ONLY with YES or NO.\n\n"
            "Say YES if the query COULD be:\n"
            "- A movie or TV series title (even partial, even if you don't recognize it)\n"
            "- An actor, actress, director, or crew member name\n"
            "- A film genre like action, horror, comedy\n"
            "- An entertainment-related keyword like 'sequel', 'animated', 'oscar winner'\n"
            "- Anything that plausibly relates to movies, shows, anime, or entertainment\n\n"
            "Say NO ONLY if the query is CLEARLY a non-entertainment everyday concept with NO plausible movie connection, "
            "such as: 'pizza', 'car engine', 'python tutorial', 'mathematics', 'weather today', 'stock market'.\n\n"
            "IMPORTANT: When in doubt, always say YES. Movie titles can be anything — 'Dune', 'Her', 'It', 'Us', 'Cars', 'Up'."
        )

        try:
            from google.genai.types import HttpOptions
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[query],
                config=types.GenerateContentConfig(
                    system_instruction=system,
                    temperature=0.0,
                    max_output_tokens=5,
                    http_options=HttpOptions(timeout=_REQUEST_TIMEOUT)
                ),
            )
            self._record_success()
            reply = response.text.strip().upper()
            # Only reject if response is unambiguously NO
            if reply.startswith("NO"):
                return False
            return True
        except Exception as e:
            self._record_failure()
            logger.error(f"Gemini anomaly during classification: {e}")
            return True  # Fail open — never block a real search due to AI error



gemini_service = GeminiService()
