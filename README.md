# Movie Recommender

AI-powered hybrid movie recommendation system with FastAPI backend and Next.js frontend.

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, SQLite
- **Frontend**: Next.js 14, TypeScript, TailwindCSS
- **ML**: Scikit-learn (TF-IDF), Surprise (SVD), Gemini AI
- **Auth**: JWT with bcrypt (Note: Short-lived access tokens used. Refresh token rotation is planned for future production parity.)

## Project Structure

```
movie-recommender/
|-- backend/              # FastAPI application
|   |-- app/
|   |   |-- api/          # REST endpoints
|   |   |-- models/       # SQLAlchemy models
|   |   |-- schemas/      # Pydantic schemas
|   |   |-- services/     # Business logic
|   |   |-- ml/           # ML training & inference
|   |   |-- config.py     # Settings
|   |   |-- database.py   # DB connection
|   |   |-- main.py       # App entry point
|   |-- data/             # SQLite database
|   |-- scripts/          # Utility scripts
|   |-- requirements.txt
|   |-- Dockerfile
|
|-- frontend/             # Next.js application
|   |-- app/              # Pages & routes
|   |-- components/       # React components
|   |-- hooks/            # Custom hooks
|   |-- lib/              # API client
|   |-- package.json
|   |-- Dockerfile
|
|-- deprecated/           # Legacy code (unused)
|-- docs/                 # Documentation
|-- tasks/                # Task tracking
|-- Makefile              # Common commands
|-- docker-compose.yml    # Container orchestration
|-- .env                  # Environment variables
|-- .gitignore
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm or yarn

### Local Development

**Development (SQLite)**:
By default, the backend uses a local SQLite database for rapid development.

```bash
# Install dependencies
make install

# Initialize database
make db-init

# Seed with sample data
make db-seed
```

**Production (PostgreSQL)**:
For production or concurrent user testing, you should use PostgreSQL. The `psycopg2-binary` driver is already installed.

1. Ensure PostgreSQL is running locally or via Docker.
2. Create a `.env` file in the `backend/` directory and set the `DATABASE_URL`:
   ```bash
   DATABASE_URL=postgresql://user:password@localhost:5432/movies_db
   ```
3. Run migrations and seed data just like SQLite:
   ```bash
   make db-init
   make db-seed
   ```

# Train ML models
make models-train

# Start backend (terminal 1)
make dev-backend

# Start frontend (terminal 2)
make dev-frontend
```

Access:
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Docker

```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/users/register` | Register user |
| POST | `/api/users/login` | Login |
| GET | `/api/users/me` | Get current user |
| GET | `/api/movies` | List movies |
| GET | `/api/movies/trending` | Trending movies |
| GET | `/api/recommendations` | Get recommendations |
| GET | `/api/recommendations/similar/{id}` | Similar movies |
| POST | `/api/chat` | AI chat assistant |

## Features

- Hybrid recommendation (content + collaborative filtering)
- AI-powered chat for movie queries
- User authentication & ratings
- Movie search & filtering
- Genre-based browsing

## License

MIT
