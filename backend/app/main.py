import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import get_settings
from app.database import engine, Base, SessionLocal
from app.api import movies, users, recommendations, chat
from app.services.hybrid_engine import hybrid_engine
from app.ml.train_models import CONTENT_MODEL_PATH, COLLAB_MODEL_PATH, get_popularity_map

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()

limiter = Limiter(key_func=get_remote_address)


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

    logger.info("Movie Recommender API started. Models loaded.")
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title="Movie Recommender API",
    description="Industry-level hybrid movie recommendation system with ML and Gemini AI",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Attach rate limiter state and handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_origin_regex=r"https://.*\.vercel\.app(-\w+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response


@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    start = time.time()
    try:
        response = await call_next(request)
        response.headers["X-Response-Time"] = f"{(time.time() - start) * 1000:.0f}ms"
        return response
    except Exception:
        logger.exception("Unhandled exception during request")
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
