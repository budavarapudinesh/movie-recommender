import os
import re

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from train_cf import load_model as load_cf_model, predict as cf_predict
from train_content import load_model as load_content_model


RATINGS_PATH = os.path.join(os.path.dirname(__file__), "data", "ratings.csv")

CF_WEIGHT = 0.7
CONTENT_WEIGHT = 0.3


def _load_ratings():
    return pd.read_csv(RATINGS_PATH)


def _get_user_rated_movies(ratings_df, user_id):
    return ratings_df[ratings_df["userId"] == user_id]


def _normalize(scores):
    min_s, max_s = scores.min(), scores.max()
    if max_s == min_s:
        return np.zeros_like(scores)
    return (scores - min_s) / (max_s - min_s)


def _parse_year(title):
    match = re.search(r"\((\d{4})\)\s*$", title)
    return int(match.group(1)) if match else None


def _clean_title(title):
    return re.sub(r"\s*\(\d{4}\)\s*$", "", title).strip()


def recommend(user_id, top_n=10):
    cf_model, trainset = load_cf_model()
    tfidf_matrix, movies_df = load_content_model()
    ratings_df = _load_ratings()

    user_rated = _get_user_rated_movies(ratings_df, user_id)
    rated_movie_ids = set(user_rated["movieId"].tolist())
    all_movie_ids = set(movies_df["movieId"].tolist())
    candidate_ids = list(all_movie_ids - rated_movie_ids)

    if not candidate_ids:
        return []

    movie_id_to_idx = {mid: idx for idx, mid in enumerate(movies_df["movieId"])}

    top_rated = user_rated[user_rated["rating"] >= 4.0]
    top_rated_indices = [
        movie_id_to_idx[mid]
        for mid in top_rated["movieId"]
        if mid in movie_id_to_idx
    ]

    cf_scores = np.array([cf_predict(cf_model, user_id, mid) for mid in candidate_ids])

    content_scores = np.zeros(len(candidate_ids))
    if top_rated_indices:
        top_rated_vecs = tfidf_matrix[top_rated_indices]
        for i, mid in enumerate(candidate_ids):
            if mid in movie_id_to_idx:
                idx = movie_id_to_idx[mid]
                sims = cosine_similarity(tfidf_matrix[idx], top_rated_vecs).flatten()
                content_scores[i] = np.mean(sims)

    cf_norm = _normalize(cf_scores)
    content_norm = _normalize(content_scores)
    hybrid_scores = CF_WEIGHT * cf_norm + CONTENT_WEIGHT * content_norm

    top_indices = np.argsort(hybrid_scores)[::-1][:top_n]
    top_movie_ids = [candidate_ids[i] for i in top_indices]

    id_to_title = dict(zip(movies_df["movieId"], movies_df["title"]))
    return [id_to_title.get(mid, f"Movie {mid}") for mid in top_movie_ids]


def recommend_rich(genres=None, year_min=1970, rating_min=0.0, top_n=6, user_id=1):
    cf_model, trainset = load_cf_model()
    tfidf_matrix, movies_df = load_content_model()
    ratings_df = _load_ratings()

    avg_ratings = ratings_df.groupby("movieId")["rating"].mean()
    rating_counts = ratings_df.groupby("movieId")["rating"].count()

    movies = movies_df.copy()
    movies["year"] = movies["title"].apply(_parse_year)
    movies["clean_title"] = movies["title"].apply(_clean_title)
    movies["genres_list"] = movies["genres"].apply(lambda g: g.split(" "))
    movies["avg_rating"] = movies["movieId"].map(avg_ratings).fillna(0)
    movies["rating_count"] = movies["movieId"].map(rating_counts).fillna(0)

    mask = movies["rating_count"] >= 10
    if year_min:
        mask &= movies["year"].fillna(0) >= year_min
    if rating_min and rating_min > 0:
        scaled_min = rating_min / 2.0
        mask &= movies["avg_rating"] >= scaled_min

    genre_map = {
        "Sci-Fi": "Sci-Fi", "Thriller": "Thriller", "Horror": "Horror",
        "Romance": "Romance", "Drama": "Drama", "Action": "Action",
        "Documentary": "Documentary", "Animated": "Animation",
        "Animation": "Animation", "Cult Classic": "Film-Noir",
        "New Release": None, "Mind-bending": "Sci-Fi",
        "Feel-good": "Comedy", "Comedy": "Comedy", "Crime": "Crime",
        "Adventure": "Adventure", "Fantasy": "Fantasy", "War": "War",
        "Mystery": "Mystery", "Musical": "Musical", "Western": "Western",
        "Children": "Children", "IMAX": "IMAX", "History": "War",
    }

    if genres:
        mapped = set()
        for g in genres:
            ml_genre = genre_map.get(g, g)
            if ml_genre:
                mapped.add(ml_genre)
        if mapped:
            mask &= movies["genres_list"].apply(lambda gl: bool(set(gl) & mapped))

    candidates = movies[mask].copy()

    if candidates.empty:
        candidates = movies[movies["rating_count"] >= 10].head(top_n * 3)

    candidate_ids = candidates["movieId"].tolist()
    movie_id_to_idx = {mid: idx for idx, mid in enumerate(movies_df["movieId"])}

    cf_scores = np.array([cf_predict(cf_model, user_id, mid) for mid in candidate_ids])

    content_scores = np.zeros(len(candidate_ids))
    if genres:
        mapped_genres = set()
        for g in genres:
            ml_g = genre_map.get(g, g)
            if ml_g:
                mapped_genres.add(ml_g)

        genre_bonus = np.array([
            len(set(candidates.iloc[i]["genres_list"]) & mapped_genres) / max(len(mapped_genres), 1)
            for i in range(len(candidate_ids))
        ])
        content_scores = genre_bonus

    cf_norm = _normalize(cf_scores)
    content_norm = _normalize(content_scores)
    hybrid_scores = CF_WEIGHT * cf_norm + CONTENT_WEIGHT * content_norm

    top_indices = np.argsort(hybrid_scores)[::-1][:top_n]

    results = []
    for i in top_indices:
        row = candidates.iloc[i]
        match_pct = int(round(hybrid_scores[i] * 100))
        match_pct = max(60, min(99, match_pct))
        avg_r = round(float(row["avg_rating"]) * 2, 1)
        results.append({
            "title": row["clean_title"],
            "year": int(row["year"]) if pd.notna(row["year"]) else None,
            "genres": row["genres_list"],
            "director": None,
            "rating": avg_r,
            "logline": None,
            "match_score": match_pct,
            "poster_url": None,
        })

    return results


if __name__ == "__main__":
    user_id = 1
    results = recommend(user_id, top_n=10)
    print(f"\nTop 10 recommendations for user {user_id}:")
    for i, title in enumerate(results, 1):
        print(f"  {i}. {title}")

