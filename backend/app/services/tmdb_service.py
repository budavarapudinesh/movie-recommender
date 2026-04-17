"""TMDB API service for fetching movie metadata, posters, and watch providers."""
import logging

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p"


class TMDBService:
    def __init__(self):
        self.api_key = get_settings().tmdb_api_key

    def _has_key(self) -> bool:
        return bool(self.api_key)

    def get_movie_details(self, tmdb_id: int) -> dict:
        """Fetch movie details including poster_path and backdrop_path."""
        if not self._has_key():
            return {}
        try:
            with httpx.Client(timeout=10) as client:
                r = client.get(
                    f"{TMDB_BASE}/movie/{tmdb_id}",
                    params={"api_key": self.api_key},
                )
                r.raise_for_status()
                return r.json()
        except Exception as e:
            logger.warning(f"TMDB fetch failed for {tmdb_id}: {e}")
            return {}

    def get_watch_providers(self, tmdb_id: int, country: str = "US") -> list[dict]:
        """Fetch watch providers (Netflix, Prime, etc.) for a movie."""
        if not self._has_key():
            return []
        try:
            with httpx.Client(timeout=10) as client:
                r = client.get(
                    f"{TMDB_BASE}/movie/{tmdb_id}/watch/providers",
                    params={"api_key": self.api_key},
                )
                r.raise_for_status()
                data = r.json().get("results", {}).get(country, {})
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
        except Exception as e:
            logger.warning(f"TMDB providers fetch failed for {tmdb_id}: {e}")
            return []

    def get_movie_videos(self, tmdb_id: int) -> str:
        """Return YouTube trailer URL if available."""
        if not self._has_key():
            return ""
        try:
            with httpx.Client(timeout=10) as client:
                r = client.get(
                    f"{TMDB_BASE}/movie/{tmdb_id}/videos",
                    params={"api_key": self.api_key},
                )
                r.raise_for_status()
                results = r.json().get("results", [])
                for v in results:
                    if v.get("site") == "YouTube" and v.get("type") == "Trailer":
                        return f"https://www.youtube.com/watch?v={v['key']}"
                return ""
        except Exception as e:
            logger.warning(f"TMDB videos fetch failed for {tmdb_id}: {e}")
            return ""


tmdb_service = TMDBService()
