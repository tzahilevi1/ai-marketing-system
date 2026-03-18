# AI Marketing System

Full-stack AI-powered marketing automation platform.

## Tech Stack
- Backend: Python 3.11+, FastAPI, SQLAlchemy 2.0, Celery, Redis, PostgreSQL
- AI: Anthropic SDK — always use model `claude-sonnet-4-20250514`
- Frontend: React 18, TypeScript, Vite, Tailwind CSS, shadcn/ui, Recharts
- Storage: AWS S3 via boto3
- Image Generation: Replicate (Flux model)

## Key Rules
1. Always use `claude-sonnet-4-20250514` for all API calls
2. Use streaming for content generation (real-time UI updates)
3. Use tool_use for structured outputs from agents
4. All API calls have retry logic with exponential backoff
5. Log all AI decisions to `ai_insights` table
6. Full mypy compliance — type hints everywhere

## Running the project
```bash
docker compose up -d postgres redis
cd backend && alembic upgrade head
uvicorn main:app --reload
celery -A tasks.tasks worker --loglevel=info
cd ../frontend && npm run dev
```

## Testing
```bash
pytest backend/tests/ -v --cov=backend
cd frontend && npm run test
```
