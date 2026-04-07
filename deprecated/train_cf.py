import os
import pickle

import pandas as pd
from surprise import SVD, Dataset, Reader, accuracy
from surprise.model_selection import train_test_split


DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "ratings.csv")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "cf_model.pkl")

SAMPLE_SIZE = int(os.environ.get("SAMPLE_SIZE", 0))


def load_data(sample_size=None):
    df = pd.read_csv(DATA_PATH)
    if sample_size and sample_size > 0 and sample_size < len(df):
        df = df.sample(n=sample_size, random_state=42)
        print(f"Sampled {sample_size:,} ratings from {len(pd.read_csv(DATA_PATH)):,} total")
    else:
        print(f"Loaded {len(df):,} ratings")
    reader = Reader(rating_scale=(0.5, 5.0))
    data = Dataset.load_from_df(df[["userId", "movieId", "rating"]], reader)
    return data, df


def train(data, test_size=0.2, random_state=42):
    trainset, testset = train_test_split(data, test_size=test_size, random_state=random_state)
    model = SVD(n_factors=100, n_epochs=20, lr_all=0.005, reg_all=0.02, random_state=random_state)
    model.fit(trainset)
    predictions = model.test(testset)
    rmse = accuracy.rmse(predictions, verbose=True)
    return model, trainset, testset, predictions, rmse


def save_model(model, trainset):
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump({"model": model, "trainset": trainset}, f)
    print(f"Collaborative filtering model saved to {MODEL_PATH}")


def load_model():
    with open(MODEL_PATH, "rb") as f:
        data = pickle.load(f)
    return data["model"], data["trainset"]


def predict(model, user_id, movie_id):
    return model.predict(user_id, movie_id).est


if __name__ == "__main__":
    sample = SAMPLE_SIZE if SAMPLE_SIZE > 0 else None
    data, ratings_df = load_data(sample_size=sample)
    model, trainset, testset, predictions, rmse = train(data)
    save_model(model, trainset)
    print(f"\nTraining complete — RMSE: {rmse:.4f}")
