"""TMDB API service for fetching movie metadata, posters, and watch providers.

Uses Python stdlib urllib to avoid httpx/requests TLS fingerprinting issues with TMDB's CDN.
"""
import json
import logging
import ssl
import urllib.request
import urllib.parse
from typing import Any

from app.config import get_settings

logger = logging.getLogger(__name__)

TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p"

# Use default SSL context with proper certificate verification
_SSL_CTX = ssl.create_default_context()


class TMDBService:
    def __init__(self):
        self.api_key = get_settings().tmdb_api_key

    def _has_key(self) -> bool:
        return bool(self.api_key)

    def _get(self, path: str, params: dict | None = None) -> dict | list | None:
        """Make a GET request to the TMDB API using stdlib urllib."""
        if not self._has_key():
            return None
        p = {"api_key": self.api_key}
        if params:
            p.update(params)
        url = f"{TMDB_BASE}/{path.lstrip('/')}?{urllib.parse.urlencode(p)}"
        try:
            req = urllib.request.urlopen(url, context=_SSL_CTX, timeout=15)
            return json.loads(req.read().decode("utf-8"))
        except Exception as e:
            logger.warning(f"TMDB fetch failed for {path}: {e}")
            return None

    def get_movie_details(self, tmdb_id: int) -> dict:
        """Fetch movie details including poster_path and backdrop_path."""
        result = self._get(f"movie/{tmdb_id}")
        return result if isinstance(result, dict) else {}

    def search_movies(self, query: str, page: int = 1) -> list[dict]:
        """Search TMDB for movies/TV by title — returns live results in all languages."""
        result = self._get("search/multi", {"query": query, "page": page})
        if isinstance(result, dict):
            return result.get("results", [])
        return []

    def get_now_playing(self, page: int = 1) -> list[dict]:
        """Get movies currently in theatres."""
        result = self._get("movie/now_playing", {"page": page, "language": "en-US"})
        if isinstance(result, dict):
            return result.get("results", [])
        return []

    def get_upcoming(self, page: int = 1) -> list[dict]:
        """Get upcoming movie releases."""
        result = self._get("movie/upcoming", {"page": page, "language": "en-US"})
        if isinstance(result, dict):
            return result.get("results", [])
        return []

    def get_watch_providers(self, tmdb_id: int, country: str = "US") -> list[dict]:
        """Fetch watch providers (Netflix, Prime, etc.) for a movie."""
        result = self._get(f"movie/{tmdb_id}/watch/providers")
        if not isinstance(result, dict):
            return []
        data = result.get("results", {}).get(country, {})
        providers = []
        for type_ in ["flatrate", "free", "ads", "rent", "buy"]:
            for p in data.get(type_, []):
                providers.append({
                    "provider_id": p["provider_id"],
                    "provider_name": p["provider_name"],
                    "logo_path": p.get("logo_path", ""),
                    "type": type_,
                    "link": data.get(
                        "link",
                        f"https://www.justwatch.com/us/search?q={tmdb_id}",
                    ),
                })
        # Deduplicate by provider_id
        seen: set[int] = set()
        unique = []
        for p in providers:
            if p["provider_id"] not in seen:
                seen.add(p["provider_id"])
                unique.append(p)
        return unique

    def get_movie_videos(self, tmdb_id: int) -> str:
        """Return YouTube trailer URL if available."""
        result = self._get(f"movie/{tmdb_id}/videos")
        if not isinstance(result, dict):
            return ""
        for v in result.get("results", []):
            if v.get("site") == "YouTube" and v.get("type") == "Trailer":
                return f"https://www.youtube.com/watch?v={v['key']}"
        return ""

    def discover_recent(self, year: int, page: int = 1) -> list[dict]:
        """Get popular movies released in a specific year."""
        result = self._get("discover/movie", {
            "sort_by": "popularity.desc",
            "primary_release_year": year,
            "page": page,
            "vote_count.gte": 50,
            "language": "en-US",
        })
        if isinstance(result, dict):
            return result.get("results", [])
        return []

    def get_recommendations_tmdb(self, tmdb_id: int, page: int = 1) -> list[dict]:
        """Get TMDB-powered recommendations for a movie."""
        result = self._get(f"movie/{tmdb_id}/recommendations", {"page": page, "language": "en-US"})
        if isinstance(result, dict):
            return result.get("results", [])
        return []

    def get_similar_tmdb(self, tmdb_id: int, page: int = 1) -> list[dict]:
        """Get similar movies from TMDB."""
        result = self._get(f"movie/{tmdb_id}/similar", {"page": page, "language": "en-US"})
        if isinstance(result, dict):
            return result.get("results", [])
        return []

    def get_trending_week(self, page: int = 1) -> list[dict]:
        """Get trending movies this week."""
        result = self._get("trending/movie/week", {"page": page, "language": "en-US"})
        if isinstance(result, dict):
            return result.get("results", [])
        return []

    def get_popular(self, page: int = 1) -> list[dict]:
        """Get popular movies."""
        result = self._get("movie/popular", {"page": page, "language": "en-US"})
        if isinstance(result, dict):
            return result.get("results", [])
        return []


tmdb_service = TMDBService()
