# Project Review & Optimization Plan

## Overview
Full codebase review for movie-recommender project (FastAPI + Next.js + ML)

## Tasks

### Phase 1: Backend Review
- [ ] **Security Audit**
  - Check hardcoded secrets in config.py
  - Verify CORS settings (currently allows localhost only - good)
  - Review JWT implementation
  - Check password hashing (bcrypt - good)
  - SQL injection prevention (SQLAlchemy ORM - safe)

- [ ] **Error Handling**
  - Review middleware error handling
  - Check database connection handling
  - Verify model loading error handling

- [ ] **Code Quality**
  - Check for code duplication
  - Review function complexity
  - Check type hints completeness

### Phase 2: Frontend Review
- [ ] **Security**
  - Check token storage (localStorage - potential XSS risk)
  - Verify API calls don't expose sensitive data

- [ ] **Code Quality**
  - Review component structure
  - Check error handling in API calls

### Phase 3: ML/Training Review
- [ ] Check model loading paths
- [ ] Verify error handling in training scripts
- [ ] Review data processing logic

### Phase 4: File Organization
- [ ] Identify redundant files
- [ ] Check for misplaced files
- [ ] Verify import paths consistency

## Status
- [x] Plan created - COMPLETED
- [x] Backend review - COMPLETED
- [x] Frontend review - COMPLETED
- [x] ML review - COMPLETED
- [x] Optimization - COMPLETED

## Issues Fixed

### Security
- Added `.gitignore` to prevent secrets in repo
- Fixed weak default SECRET_KEY in config.py (now auto-generates)
- Fixed permissive CORS in legacy api/main.py

### Performance
- Optimized gemini_service._extract_movie_ids() to use top 500 movies instead of ALL

### Code Organization
- Created tasks/todo.md and tasks/lessons.md for tracking

## Notes
- Project uses SQLite for local dev
- JWT auth with bcrypt
- Hybrid recommendation engine (content + collaborative)
- Gemini AI integration for chat
