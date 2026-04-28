# Project Lessons & Agent Rules

## Workflow Orchestration

### 1. Plan Mode Default
- Enter plan mode for ANY non-trivial task (3+ steps or architectural decisions).
- If something goes sideways, STOP and re-plan immediately - don't keep pushing.
- Use plan mode for verification steps, not just building.
- Write detailed specs upfront to reduce ambiguity.

### 2. Subagent Strategy
- Use subagents liberally to keep main context window clean.
- Offload research, exploration, and parallel analysis to subagents.
- For complex problems, throw more compute at it via subagents.
- One task per subagent for focused execution.

### 3. Self-Improvement Loop
- After ANY correction from the user: update tasks/lessons.md with the pattern.
- Write rules for yourself that prevent the same mistake.
- Ruthlessly iterate on these lessons until mistake rate drops.
- Review lessons at session start for relevant project.

### 4. Verification Before Done
- Never mark a task complete without proving it works.
- Diff behavior between main and your changes when relevant.
- Ask yourself: "Would a staff engineer approve this?"
- Run tests, check logs, demonstrate correctness.

### 5. Demand Elegance (Balanced)
- For non-trivial changes: pause and ask "is there a more elegant way?"
- If a fix feels hacky: "Knowing everything I know now, implement the elegant solution"
- Skip this for simple, obvious fixes - don't over-engineer.
- Challenge your own work before presenting it.

### 6. Autonomous Bug Fixing
- When given a bug report: just fix it. Don't ask for hand-holding.
- Point at logs, errors, failing tests - then resolve them.
- Zero context switching required from the user.
- Go fix failing CI tests without being told how.

## Task Management
- **Plan First**: Write plan to `tasks/todo.md` with checkable items.
- **Verify Plan**: Check in before starting implementation.
- **Track Progress**: Mark items complete as you go.
- **Explain Changes**: High-level summary at each step.
- **Document Results**: Add review section to `tasks/todo.md`.
- **Capture Lessons**: Update `tasks/lessons.md` after corrections.

## Core Principles
- **Simplicity First**: Make every change as simple as possible. Impact minimal code.
- **No Laziness**: Find root causes. No temporary fixes. Senior developer standards.
- **Minimal Impact**: Changes should only touch what's necessary. Avoid introducing bugs.

---

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
