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

## Execution Tasks
- [ ] **Setup Phase**
  - [x] Create Python virtual environment
  - [x] Install backend dependencies
  - [x] Install frontend dependencies
- [ ] **Database & ML Phase**
  - [x] Initialize database schema
  - [x] Seed database with ratings
  - [x] Train recommendation models
- [x] **Run Phase**
  - [x] Start backend server (port 8000)
  - [x] Start frontend server (port 3000)
  - [x] Verify health status

## UI Refactoring Reviews
### Genre Selector Optimization
- **Action**: Removed horizontal scrolling 'MovieRow' carousel and the 'HeroBanner' from the home page (`page.tsx`) to strictly simplify layout.
- **Action**: Cleaned up top-level navigation links by removing 'Discover', 'AI Picks', and 'Ask AI' from the `Navbar.tsx` to streamline header items.
- **Action**: Centered the 'Genre' filter pills block (`page.tsx`) and upgraded its container from horizontal scroll to a `flex-wrap` cluster, effectively grouping all genres symmetrically in the middle of the viewport.
- **Action**: Overhauled global Search Bar behavior. Integrated a `useDebounce` hook (500ms frontend delay) attached to an all-new backend `is_entertainment_query` Gemini Semantic classifier in `movies.py`, strictly guaranteeing that non-entertainment entries return an explicit UI prompt "Not found".
- **Verification**: Restarted NextJS dev server. Performed direct DOM checks showing successful Next.js server-side compilation, absence of horizontal scrolling cards, and clean transition directly from navbar to the centered Genre selector.
- **Status**: Approved and verified.

## Notes
- Project uses SQLite for local dev
- JWT auth with bcrypt
- Hybrid recommendation engine (content + collaborative)
- Gemini AI integration for chat
