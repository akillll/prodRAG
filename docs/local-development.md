# Local Development

This project is intentionally local-first. The current work is Sprint 2: document ingestion
and storage. PostgreSQL with pgvector is the only required service.

## Prerequisites

Install:

* Python 3.13
* Node.js 22 or newer
* Git

Optional but useful:

* `psql`, the PostgreSQL command-line client

For the current local setup, PostgreSQL runs directly on your machine through the Homebrew installation rather than Docker.

## Environment setup

From the repository root:

```bash
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
```

Add your OpenAI API key to `.env` and `backend/.env` when model calls are implemented.
`frontend/.env.local` defaults to the local FastAPI server at `http://127.0.0.1:8000`.

## Backend setup

```bash
cd backend
source venv/bin/activate
python -m pip install -r requirements-dev.txt
```

Run tests:

```bash
python -m pytest tests
```

Run linting when you want a quick hygiene check:

```bash
ruff check src tests
```

Start the API:

```bash
uvicorn main:app --app-dir src --reload
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Readiness check, including database connectivity:

```bash
curl http://127.0.0.1:8000/ready
```

## Database setup

Start PostgreSQL:

```bash
brew services start postgresql@17
```

Run migrations:

```bash
cd backend
source venv/bin/activate
alembic -c migrations/alembic.ini upgrade head
```

Verify pgvector:

```bash
psql prodrag -c "SELECT extname FROM pg_extension WHERE extname = 'vector';"
```

Stop PostgreSQL:

```bash
brew services stop postgresql@17
```

## Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Type-check:

```bash
npm run typecheck
```

Lint:

```bash
npm run lint
```

## Common workflow

Terminal 1:

```bash
brew services start postgresql@17
```

Terminal 2:

```bash
cd backend
source venv/bin/activate
uvicorn main:app --app-dir src --reload
```

Terminal 3:

```bash
cd frontend
npm run dev
```
