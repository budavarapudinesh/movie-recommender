# Code Review Lessons

## Critical Security Issues Found

### 1. Hardcoded API Key in .env
- **File**: `backend/.env`
- **Issue**: GEMINI_API_KEY is hardcoded directly in the file
- **Risk**: API key exposed if repo is public
- **Fix**: Use environment variables or secrets management

### 2. Weak Default Secret Key
- **File**: `backend/app/config.py:14`
- **Issue**: Default SECRET_KEY = "dev-secret-key-change-in-production"
- **Risk**: Weak JWT signing key allows token forgery
- **Fix**: Generate strong random key for production

### 3. Permissive CORS in Legacy API
- **File**: `api/main.py:21`
- **Issue**: `allow_origins=["*"]` allows any domain
- **Risk**: Cross-site request forgery
- **Fix**: Restrict to specific origins

## Performance Issues

### 4. Loading All Movies for Title Matching
- **File**: `backend/app/services/gemini_service.py:122`
- **Issue**: `_extract_movie_ids()` loads ALL movies from DB
- **Impact**: O(n) memory and query time for every chat message
- **Fix**: Use full-text search or limit to popular titles

## Code Organization Issues

### 5. Duplicate Legacy Code at Root Level
- **Files**: `recommend.py`, `train_cf.py`, `train_content.py`, `train_two_tower.py`, `api/`, `data/`, `models/`
- **Issue**: Duplicate system using CSV files vs backend using SQLite
- **Impact**: Confusion, maintenance burden, potential wrong file usage
- **Fix**: Remove or clearly mark as deprecated

## Recommendations

1. **Add .env to .gitignore** if not already there
2. **Generate strong SECRET_KEY** on first startup
3. **Remove legacy root-level files** or move to `legacy/` folder
4. **Optimize movie title search** with database-level filtering
5. **Add input validation** for search endpoints
