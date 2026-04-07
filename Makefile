.PHONY: help install dev-backend dev-frontend test clean db-init db-seed models-train

help:
	@echo "Available commands:"
	@echo "  make install        - Install all dependencies"
	@echo "  make dev-backend    - Start backend dev server"
	@echo "  make dev-frontend   - Start frontend dev server"
	@echo "  make test           - Run tests"
	@echo "  make clean          - Clean cache files"
	@echo "  make db-init        - Initialize database"
	@echo "  make db-seed        - Seed database with data"
	@echo "  make models-train   - Train ML models"

install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

dev-backend:
	cd backend && python3.11 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && npm run dev

test:
	cd backend && python3.11 -m pytest

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf frontend/.next

db-init:
	cd backend && python3.11 -c "from app.database import engine, Base; Base.metadata.create_all(bind=engine)"

db-seed:
	cd backend && python3.11 scripts/seed_ratings.py

models-train:
	cd backend && python3.11 -m app.ml.train_models
