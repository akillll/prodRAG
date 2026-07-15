# ADR-002: Local PostgreSQL Over Docker

* Related tasks: `FND-006`, `FND-007`, `FND-010`

## Context

prodRAG is a local, single-user learning project. The main goal is to understand and implement the core RAG pipeline, not to demonstrate container orchestration or environment management patterns.

The project requires PostgreSQL with `pgvector` and `pg_trgm`. There were multiple viable setup options:

1. PostgreSQL in Docker
2. PostgreSQL installed locally through Homebrew
3. A dedicated database role for the application
4. Reusing the local administrative user for development

Docker would improve isolation and make the environment more portable, but it would also add another toolchain and more setup/debugging surface area. A dedicated database role would more closely resemble production setup, but it adds administrative steps without improving the RAG implementation itself.

## Decision

The default local development setup uses:

1. PostgreSQL 17 installed through Homebrew
2. A local `prodrag` database
3. The existing local PostgreSQL user through a Unix socket connection
4. `pgvector` and `pg_trgm` enabled in the local database

The default local connection string is:

```text
postgresql+psycopg:///prodrag
```

This avoids Docker and avoids creating a separate application role for the first release.

## Rationale

This decision keeps the local setup aligned with the stated project scope:

* local-first
* single-user
* minimal infrastructure
* focus on ingestion, retrieval, citations, and evaluation

The Homebrew setup reduces friction in daily development:

* fewer moving parts during backend work
* easier use of `psql`, Alembic, and local inspection commands
* simpler documentation for a reviewer running the project locally
* less time spent on container and networking issues

Using the local PostgreSQL user is acceptable because this is not a multi-user or production deployment.

## Consequences

### Benefits

* Faster local setup for this project.
* Less infrastructure complexity around migrations and debugging.
* Direct use of local PostgreSQL tools such as `psql`.
* Fewer environment variables and credential-management steps.

### Costs

* Lower isolation than a containerized database.
* Setup is more machine-specific than Docker.
* The local administrative user is not a production-style security model.
* Reviewers on non-Homebrew systems may need slight setup adjustments.

## Rejected alternatives

### Docker as the default

Rejected for the first release because it adds complexity that does not improve the core learning goal. The repo may still keep Docker artifacts for optional future use or comparison.

### Dedicated application role

Rejected for the first release because it introduces more local database administration while providing little practical value for a single-user portfolio project.

## Revisit conditions

This decision should be revisited if any of the following become true:

* multiple contributors need a uniform database environment
* CI starts running database-backed integration tests in containers
* the project is prepared for public deployment rather than local demonstration
* role-based access and stricter local security boundaries become relevant

## Completion criteria

`ADR-002` is complete when:

* the repository documents Homebrew PostgreSQL as the default local setup
* the local connection string is socket-based
* migrations run successfully against the local PostgreSQL 17 database
* the project no longer assumes Docker or a separate application role for standard local development
