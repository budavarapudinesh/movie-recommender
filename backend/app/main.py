import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import engine, Base, SessionLocal
from app.api import movies, users, recommendations, chat
from app.services.hybrid_engine import hybrid_engine
from app.ml.train_models import CONTENT_MODEL_PATH, COLLAB_MODEL_PATH, get_popularity_map


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables and load models
    Base.metadata.create_all(bind=engine)

    # Load pre-trained models if they exist
    hybrid_engine.load_models(CONTENT_MODEL_PATH, COLLAB_MODEL_PATH)

    # Load popularity scores
    db = SessionLocal()
    try:
        hybrid_engine.set_popularity(get_popularity_map(db))
    finally:
        db.close()

    print("Movie Recommender API started. Models loaded.")
    yield
    print("Shutting down.")


app = FastAPI(
    title="Movie Recommender API",
    description="Industry-level hybrid movie recommendation system with ML and Gemini AI",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    start = time.time()
    try:
        response = await call_next(request)
        response.headers["X-Response-Time"] = f"{(time.time() - start) * 1000:.0f}ms"
        return response
    except Exception:
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(movies.router)
app.include_router(users.router)
app.include_router(recommendations.router)
app.include_router(chat.router)


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "content_model_loaded": hybrid_engine.content_engine.tfidf_matrix is not None,
        "collab_model_loaded": hybrid_engine.collab_engine.is_trained,
    }
