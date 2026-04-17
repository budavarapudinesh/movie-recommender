"""Add watch_providers, content_type, trailer_url columns to movies table."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import engine
from sqlalchemy import text


def migrate():
    with engine.connect() as conn:
        for col, definition in [
            ("watch_providers", "TEXT DEFAULT '[]'"),
            ("content_type", "VARCHAR(20) DEFAULT 'movie'"),
            ("trailer_url", "VARCHAR(500) DEFAULT ''"),
        ]:
            try:
                conn.execute(text(f"ALTER TABLE movies ADD COLUMN {col} {definition}"))
                print(f"Added column: {col}")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    print(f"Column {col} already exists, skipping")
                else:
                    raise
        conn.commit()
        print("Migration complete!")


if __name__ == "__main__":
    migrate()
