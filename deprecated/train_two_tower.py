import os
import pickle

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset


DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "ratings.csv")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "two_tower_model.pt")
METADATA_PATH = os.path.join(os.path.dirname(__file__), "models", "two_tower_meta.pkl")


class RatingsDataset(Dataset):
    def __init__(self, user_ids, movie_ids, ratings):
        self.user_ids = torch.LongTensor(user_ids)
        self.movie_ids = torch.LongTensor(movie_ids)
        self.ratings = torch.FloatTensor(ratings)

    def __len__(self):
        return len(self.ratings)

    def __getitem__(self, idx):
        return self.user_ids[idx], self.movie_ids[idx], self.ratings[idx]


class TwoTowerModel(nn.Module):
    def __init__(self, n_users, n_movies, embedding_dim=64, hidden_dim=128):
        super().__init__()
        self.user_tower = nn.Sequential(
            nn.Embedding(n_users, embedding_dim),
        )
        self.user_mlp = nn.Sequential(
            nn.Linear(embedding_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, embedding_dim),
        )
        self.movie_tower = nn.Sequential(
            nn.Embedding(n_movies, embedding_dim),
        )
        self.movie_mlp = nn.Sequential(
            nn.Linear(embedding_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, embedding_dim),
        )
        self.output_bias = nn.Parameter(torch.zeros(1))

    def forward(self, user_ids, movie_ids):
        user_emb = self.user_tower[0](user_ids)
        user_repr = self.user_mlp(user_emb)

        movie_emb = self.movie_tower[0](movie_ids)
        movie_repr = self.movie_mlp(movie_emb)

        dot = (user_repr * movie_repr).sum(dim=1)
        return dot + self.output_bias


SAMPLE_SIZE = int(os.environ.get("SAMPLE_SIZE", 0))


def load_and_prepare_data():
    df = pd.read_csv(DATA_PATH)
    if SAMPLE_SIZE > 0 and SAMPLE_SIZE < len(df):
        df = df.sample(n=SAMPLE_SIZE, random_state=42)
        print(f"Sampled {SAMPLE_SIZE:,} ratings")
    else:
        print(f"Loaded {len(df):,} ratings")

    user_ids = df["userId"].values
    movie_ids = df["movieId"].values
    ratings = df["rating"].values

    unique_users = np.unique(user_ids)
    unique_movies = np.unique(movie_ids)

    user_map = {uid: idx for idx, uid in enumerate(unique_users)}
    movie_map = {mid: idx for idx, mid in enumerate(unique_movies)}

    mapped_users = np.array([user_map[u] for u in user_ids])
    mapped_movies = np.array([movie_map[m] for m in movie_ids])

    return mapped_users, mapped_movies, ratings, user_map, movie_map


def train(epochs=10, batch_size=4096, lr=1e-3, embedding_dim=64, hidden_dim=128):
    mapped_users, mapped_movies, ratings, user_map, movie_map = load_and_prepare_data()

    n_users = len(user_map)
    n_movies = len(movie_map)

    split_idx = int(len(ratings) * 0.8)
    indices = np.random.RandomState(42).permutation(len(ratings))
    train_idx, val_idx = indices[:split_idx], indices[split_idx:]

    train_dataset = RatingsDataset(mapped_users[train_idx], mapped_movies[train_idx], ratings[train_idx])
    val_dataset = RatingsDataset(mapped_users[val_idx], mapped_movies[val_idx], ratings[val_idx])

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = TwoTowerModel(n_users, n_movies, embedding_dim, hidden_dim).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-5)
    criterion = nn.MSELoss()

    for epoch in range(epochs):
        model.train()
        train_loss = 0.0
        for users, movies, rats in train_loader:
            users, movies, rats = users.to(device), movies.to(device), rats.to(device)
            optimizer.zero_grad()
            preds = model(users, movies)
            loss = criterion(preds, rats)
            loss.backward()
            optimizer.step()
            train_loss += loss.item() * len(rats)
        train_loss /= len(train_dataset)

        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for users, movies, rats in val_loader:
                users, movies, rats = users.to(device), movies.to(device), rats.to(device)
                preds = model(users, movies)
                loss = criterion(preds, rats)
                val_loss += loss.item() * len(rats)
        val_loss /= len(val_dataset)

        rmse = np.sqrt(val_loss)
        print(f"Epoch {epoch+1}/{epochs} — Train Loss: {train_loss:.4f} | Val RMSE: {rmse:.4f}")

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    torch.save(model.state_dict(), MODEL_PATH)

    with open(METADATA_PATH, "wb") as f:
        pickle.dump({
            "user_map": user_map,
            "movie_map": movie_map,
            "n_users": n_users,
            "n_movies": n_movies,
            "embedding_dim": embedding_dim,
            "hidden_dim": hidden_dim,
        }, f)

    print(f"\nTwo-tower model saved to {MODEL_PATH}")
    print(f"Metadata saved to {METADATA_PATH}")
    return model


if __name__ == "__main__":
    train()
