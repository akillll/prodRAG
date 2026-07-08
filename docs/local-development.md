# Local Development

This project is intentionally local-first. The only required service for the current foundation sprint is PostgreSQL with pgvector.

## Prerequisites

Install:

* Python 3.13
* Node.js 22 or newer
* Docker Desktop, with the Docker daemon running
* Git

Optional but useful:

* `psql`, the PostgreSQL command-line client

You do not need to install pgvector on your machine if you use Docker Compose. The Compose stack uses the `pgvector/pgvector:pg16` image, which already includes the extension.

## Environment setup

From the repository root:

```bash
cp .env.example .env
cp backend/.env.example backend/.env
```

Add your OpenAI API key to `.env` and `backend/.env` when model calls are implemented.

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

Start PostgreSQL with pgvector:

```bash
docker compose up -d postgres
```

Run migrations:

```bash
cd backend
source venv/bin/activate
alembic -c migrations/alembic.ini upgrade head
```

Verify pgvector with local `psql` if installed:

```bash
psql "postgresql://prodrag:prodrag@localhost:5432/prodrag" -c "SELECT extname FROM pg_extension WHERE extname = 'vector';"
```

Or verify through the running container without installing local `psql`:

```bash
docker-compose exec postgres psql -U prodrag -d prodrag -c "SELECT extname FROM pg_extension WHERE extname = 'vector';"
```

Stop services:

```bash
docker compose down
```

Delete local database data:

```bash
docker compose down -v
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
docker compose up -d postgres
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
