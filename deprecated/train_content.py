import os
import pickle

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer


DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "movies.csv")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "content_model.pkl")


def load_movies():
    df = pd.read_csv(DATA_PATH)
    df["genres"] = df["genres"].str.replace("|", " ", regex=False)
    return df


def build_tfidf_matrix(movies_df):
    tfidf = TfidfVectorizer(stop_words="english")
    tfidf_matrix = tfidf.fit_transform(movies_df["genres"])
    return tfidf_matrix


def save_model(tfidf_matrix, movies_df):
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump({"tfidf_matrix": tfidf_matrix, "movies_df": movies_df}, f)
    print(f"Content-based model saved to {MODEL_PATH}")


def load_model():
    with open(MODEL_PATH, "rb") as f:
        data = pickle.load(f)
    return data["tfidf_matrix"], data["movies_df"]


def get_similarity(tfidf_matrix, idx, target_indices):
    from sklearn.metrics.pairwise import cosine_similarity
    vec = tfidf_matrix[idx]
    targets = tfidf_matrix[target_indices]
    return cosine_similarity(vec, targets).flatten()


if __name__ == "__main__":
    movies_df = load_movies()
    tfidf_matrix = build_tfidf_matrix(movies_df)
    save_model(tfidf_matrix, movies_df)
    print(f"Content model trained — {tfidf_matrix.shape[0]} movies indexed (sparse TF-IDF)")
