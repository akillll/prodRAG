# ADR-005: PostgreSQL For Vector And Lexical Search

* Related tasks: `FND-006`, `RET-002`, `IDX-001`, `IDX-002`

## Context

prodRAG needs:

1. application metadata storage
2. document and chunk persistence
3. vector similarity search
4. lexical search

There were multiple possible approaches:

1. PostgreSQL plus `pgvector` plus PostgreSQL full-text search
2. PostgreSQL plus a separate search engine
3. PostgreSQL plus a separate vector database

Using separate search systems can be powerful, but they also add operational complexity, synchronization problems, and more infrastructure to explain.

## Decision

The first release uses PostgreSQL for both retrieval modes:

1. `pgvector` for vector similarity retrieval
2. PostgreSQL full-text search for lexical retrieval

PostgreSQL is also the system of record for document metadata, versions, elements, chunks, and conversations.

## Rationale

This keeps the storage design compact and understandable:

* one database to operate locally
* no external search cluster
* no separate vector store
* easier transactional coordination during ingestion and deletion

For the scope of this project, the reduction in infrastructure complexity is more valuable than optimizing for scale that the project does not need.

## Consequences

### Benefits

* Simpler local setup.
* Easier ingestion and deletion consistency.
* Hybrid retrieval can be implemented without cross-system synchronization.
* A reviewer can understand the storage architecture quickly.

### Costs

* Lower scalability than specialized multi-system architectures.
* Less freedom to tune lexical and vector systems independently.
* Future production deployment might outgrow this design.

## Rejected alternatives

### Separate search engine plus vector store

Rejected for the first release because it adds too much operational and integration complexity for a local learning-first project.

## Revisit conditions

This decision should be revisited if:

* retrieval scale grows beyond what local PostgreSQL handles comfortably
* indexing throughput becomes a major bottleneck
* separate search capabilities become necessary for a deployment-oriented version of the project

## Completion criteria

`ADR-005` is complete when:

* PostgreSQL is the source of truth for ingestion artifacts
* vector retrieval uses `pgvector`
* lexical retrieval uses PostgreSQL full-text search
* the first release does not depend on an external search service
