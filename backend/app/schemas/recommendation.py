from pydantic import BaseModel
from app.schemas.movie import MovieBrief


class RecommendationItem(BaseModel):
    movie: MovieBrief
    score: float
    reason: str  # e.g. "Because you liked Inception"


class RecommendationResponse(BaseModel):
    recommendations: list[RecommendationItem]
    strategy: str  # "hybrid", "content_based", "popular"


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []


class ChatResponse(BaseModel):
    reply: str
    recommended_movies: list[MovieBrief] = []
