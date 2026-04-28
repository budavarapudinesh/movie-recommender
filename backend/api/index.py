"""Vercel Python serverless entry point.

Vercel discovers this file via the `api/` directory convention
and routes all requests to the FastAPI `app` instance.
"""
from app.main import app
