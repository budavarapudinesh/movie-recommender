"""Migrate movie data from local SQLite to Neon PostgreSQL.

Usage:
    cd backend
    source venv/bin/activate
    DATABASE_URL="postgresql://user:pass@host/dbname?sslmode=require" python scripts/migrate_to_postgres.py

This script:
1. Reads all movies, genres, and movie-genre associations from the local SQLite DB
2. Creates the schema in Neon PostgreSQL
3. Inserts all data using bulk inserts
"""
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import sqlite3
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

# ------------------------------------------------------------------
# Source: local SQLite
# ------------------------------------------------------------------
SQLITE_PATH = Path(__file__).resolve().parent.parent / "data" / "movies.db"

if not SQLITE_PATH.exists():
    print(f"❌ SQLite database not found at {SQLITE_PATH}")
    sys.exit(1)

# ------------------------------------------------------------------
# Target: Neon PostgreSQL (from DATABASE_URL env var)
# ------------------------------------------------------------------
PG_URL = os.environ.get("DATABASE_URL", "")
if not PG_URL or "postgresql" not in PG_URL:
    print("❌ Set DATABASE_URL env var to your Neon PostgreSQL connection string.")
    print('   Example: DATABASE_URL="postgresql://user:pass@host/dbname?sslmode=require"')
    sys.exit(1)

print(f"📦 Source: {SQLITE_PATH}")
print(f"🎯 Target: {PG_URL[:50]}...")


def migrate():
    # Connect to SQLite
    sqlite_conn = sqlite3.connect(str(SQLITE_PATH))
    sqlite_conn.row_factory = sqlite3.Row

    # Connect to PostgreSQL
    pg_engine = create_engine(PG_URL, poolclass=NullPool)

    # Import models to create tables
    from app.database import Base
    from app.models.movie import Movie, Genre, movie_genres  # noqa: F401
    from app.models.user import User  # noqa: F401
    from app.models.rating import Rating  # noqa: F401

    print("\n🔨 Creating tables in PostgreSQL...")
    Base.metadata.drop_all(bind=pg_engine)  # Clean slate
    Base.metadata.create_all(bind=pg_engine)
    print("✅ Tables created.")

    PgSession = sessionmaker(bind=pg_engine)
    pg_db = PgSession()

    try:
        # ------ Genres ------
        print("\n📋 Migrating genres...")
        genres = sqlite_conn.execute("SELECT id, name FROM genres").fetchall()
        for g in genres:
            pg_db.execute(
                text("INSERT INTO genres (id, name) VALUES (:id, :name)"),
                {"id": g["id"], "name": g["name"]},
            )
        pg_db.commit()
        print(f"   ✅ {len(genres)} genres migrated.")

        # ------ Movies ------
        print("\n🎬 Migrating movies...")
        movies = sqlite_conn.execute("SELECT * FROM movies").fetchall()
        cols = [desc[0] for desc in sqlite_conn.execute("SELECT * FROM movies LIMIT 1").description]

        batch = []
        for m in movies:
            row = {col: m[col] for col in cols}
            batch.append(row)

        if batch:
            col_list = ", ".join(cols)
            val_list = ", ".join(f":{c}" for c in cols)
            pg_db.execute(
                text(f"INSERT INTO movies ({col_list}) VALUES ({val_list})"),
                batch,
            )
            pg_db.commit()
        print(f"   ✅ {len(movies)} movies migrated.")

        # ------ Movie-Genre associations ------
        print("\n🔗 Migrating movie-genre links...")
        links = sqlite_conn.execute("SELECT movie_id, genre_id FROM movie_genres").fetchall()
        link_data = [{"movie_id": l["movie_id"], "genre_id": l["genre_id"]} for l in links]
        if link_data:
            pg_db.execute(
                text("INSERT INTO movie_genres (movie_id, genre_id) VALUES (:movie_id, :genre_id)"),
                link_data,
            )
            pg_db.commit()
        print(f"   ✅ {len(links)} movie-genre links migrated.")

        # ------ Sequences ------
        # Reset PostgreSQL auto-increment sequences to avoid ID conflicts
        print("\n🔄 Resetting sequences...")
        for table in ["movies", "genres"]:
            pg_db.execute(text(
                f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), "
                f"COALESCE((SELECT MAX(id) FROM {table}), 1))"
            ))
        pg_db.commit()
        print("   ✅ Sequences reset.")

        print("\n🎉 Migration complete!")

    except Exception as e:
        pg_db.rollback()
        print(f"\n❌ Migration failed: {e}")
        raise
    finally:
        pg_db.close()
        sqlite_conn.close()
        pg_engine.dispose()


if __name__ == "__main__":
    migrate()
