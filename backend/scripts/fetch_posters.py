"""Fetch poster paths by scraping TMDB movie pages (no API key needed)."""
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx
from app.database import SessionLocal
from app.models.movie import Movie
from app.models.user import User  # noqa: F401
from app.models.rating import Rating  # noqa: F401

OG_IMAGE_RE = re.compile(r'og:image[^>]*content="([^"]+)"')
PATH_RE = re.compile(r"/t/p/w\d+(/[^\"]+\.jpg)")
BACKDROP_RE = re.compile(r'class="backdrop"[^>]*style="[^"]*url\([^)]*(/[^)]+\.jpg)')


def fetch_posters():
    db = SessionLocal()
    client = httpx.Client(
        follow_redirects=True,
        timeout=15,
        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"},
    )

    try:
        movies = (
            db.query(Movie)
            .filter(Movie.poster_path == "")
            .order_by(Movie.popularity.desc())
            .limit(200)
            .all()
        )
        print(f"Fetching posters for {len(movies)} movies...")

        updated = 0
        errors = 0
        for i, movie in enumerate(movies):
            try:
                resp = client.get(f"https://www.themoviedb.org/movie/{movie.tmdb_id}")

                if resp.status_code == 200:
                    html = resp.text

                    # Extract poster from og:image
                    og_match = OG_IMAGE_RE.search(html)
                    if og_match:
                        path_match = PATH_RE.search(og_match.group(1))
                        if path_match:
                            movie.poster_path = path_match.group(1)
                            updated += 1

                    # Extract backdrop
                    all_imgs = re.findall(r'image\.tmdb\.org/t/p/w\d+(/[^\"\s)]+\.jpg)', html)
                    if len(all_imgs) > 1 and movie.poster_path:
                        # Second unique image is usually the backdrop
                        for img_path in all_imgs:
                            if img_path != movie.poster_path:
                                movie.backdrop_path = img_path
                                break

                elif resp.status_code == 429:
                    print(f"  Rate limited at {i}. Waiting 5s...")
                    time.sleep(5)
                    continue
                else:
                    errors += 1

                # Commit every 40 movies
                if (i + 1) % 40 == 0:
                    db.commit()
                    print(f"  [{i+1}/{len(movies)}] Updated: {updated}, Errors: {errors}")

                # Pace: ~3 req/sec to be respectful
                time.sleep(0.35)

            except Exception as e:
                errors += 1
                if errors % 20 == 0:
                    print(f"  Error #{errors} at movie '{movie.title}': {e}")
                time.sleep(1)
                continue

        db.commit()
        print(f"\nDone! Updated {updated}/{len(movies)} posters. Errors: {errors}")

    finally:
        client.close()
        db.close()


if __name__ == "__main__":
    fetch_posters()
