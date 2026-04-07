import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from recommend import recommend, recommend_rich

app = FastAPI(
    title="Movie Recommendation API",
    description="Hybrid movie recommendation system combining collaborative filtering and content-based filtering.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RecommendRequest(BaseModel):
    query: Optional[str] = None
    genres: Optional[list[str]] = None
    year_min: Optional[int] = 1970
    rating_min: Optional[float] = 0.0
    top_n: Optional[int] = 6


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/recommend/{user_id}")
def get_recommendations(user_id: int, top_n: int = Query(default=10, ge=1, le=100)):
    try:
        titles = recommend(user_id, top_n=top_n)
    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail="Models not trained yet. Run train_cf.py and train_content.py first.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if not titles:
        raise HTTPException(status_code=404, detail=f"No recommendations found for user {user_id}")

    return {"user_id": user_id, "recommendations": titles}


@app.post("/recommend")
def post_recommendations(req: RecommendRequest):
    try:
        results = recommend_rich(
            genres=req.genres,
            year_min=req.year_min or 1970,
            rating_min=req.rating_min or 0.0,
            top_n=req.top_n or 6,
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail="Models not trained yet. Run train_cf.py and train_content.py first.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "recommendations": results,
        "model_note": f"Hybrid model: 70% collaborative filtering + 30% content similarity. Filtered by genres={req.genres}, year≥{req.year_min}, rating≥{req.rating_min}."
    }
