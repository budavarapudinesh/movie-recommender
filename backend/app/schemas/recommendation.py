from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.movie import MovieBrief


class RecommendationItem(BaseModel):
    movie: MovieBrief
    score: float
    reason: str  # e.g. "Because you liked Inception"


class RecommendationResponse(BaseModel):
    recommendations: list[RecommendationItem]
    strategy: str  # "hybrid", "content_based", "popular"


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=2000)


class ChatRequest(BaseModel):
    message: str = Field(max_length=2000)
    history: list[ChatMessage] = Field(default=[], max_length=50)


class ChatResponse(BaseModel):
    reply: str
    recommended_movies: list[MovieBrief] = []
