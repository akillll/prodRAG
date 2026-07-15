# Release Notes

## v0.1

Initial local foundation.

Highlights:

1. monorepo structure with frontend and backend
2. PostgreSQL with pgvector
3. Alembic migration setup
4. basic health and readiness endpoints
5. frontend linting and type checking

At v0.1, the team considered background-job infrastructure but did not include it in the first release.

## v0.2

Scope reduction toward a learning-first RAG system.

Highlights:

1. Redis removed from the project scope
2. background workers removed from the first release
3. object storage services removed from the first release
4. frontend testing intentionally kept out of scope
5. synchronous ingestion documented as the initial execution model

## Superseded assumptions

The following statements are no longer current after v0.2:

1. The first release uses Redis for document processing.
2. The first release requires a background worker container.
3. The first release depends on object storage services.

## Current default

The current default after v0.2 is synchronous ingestion in a local, single-user application.

## Future direction

If concurrency or reliability needs change, the ingestion pipeline may later move behind a job system. That is a possible future change, not a current requirement.
