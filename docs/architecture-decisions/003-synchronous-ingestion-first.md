# ADR-003: Synchronous Ingestion First

* Related tasks: `ING-002`, `ING-004`, `ING-009`

## Context

prodRAG is a local, single-user project focused on learning the core RAG pipeline. The initial ingestion flow covers:

1. file validation
2. original file storage
3. parsing
4. chunking
5. embedding
6. indexing
7. document activation

There were two reasonable implementation approaches:

1. run ingestion synchronously inside the upload request
2. add a background worker and job queue from the start

Background processing would reduce request time and more closely resemble a production architecture, but it would also add another subsystem to build, debug, and explain.

## Decision

The first release uses synchronous ingestion.

Uploading a document runs the ingestion pipeline directly and keeps the request open until processing either succeeds or fails.

The ingestion pipeline must still remain separated from the FastAPI route layer so the execution mechanism can change later without rewriting parsing, chunking, embedding, or indexing logic.

## Rationale

This keeps the implementation aligned with the actual goal of the project:

* understand the RAG pipeline itself
* keep failures inspectable
* reduce infrastructure complexity
* avoid adding a queue before there is measured need

For a local, single-user system, longer upload requests are acceptable if they keep the architecture easier to reason about.

## Consequences

### Benefits

* Fewer moving parts in the initial system.
* Easier debugging of upload-to-ready behavior.
* Lower setup and implementation cost.
* Faster progress on parsing, chunking, and citations.

### Costs

* Upload requests may take noticeably longer.
* The UI must handle waiting states during ingestion.
* There is no built-in retry scheduler or asynchronous buffering.

## Rejected alternatives

### Background worker and queue in the first release

Rejected because the added complexity would dominate the current stage of the project without improving the core learning outcome enough to justify it.

## Revisit conditions

This decision should be revisited if any of the following become true:

* ingestion latency becomes disruptive during normal development
* concurrent users or repeated uploads need buffering
* retries, durability, or job isolation become important design goals

## Completion criteria

`ADR-003` is complete when:

* upload processing is documented as synchronous
* the backend keeps ingestion logic separate from the API route
* the first release does not depend on Redis, Celery, Dramatiq, or another job system
