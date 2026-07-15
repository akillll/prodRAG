# ADR-001: Backend Module Boundaries

* Related task: `FND-002`

## Context

prodRAG contains document ingestion, parsing, chunking, embedding, retrieval, reranking, context assembly, generation, citation validation, evaluation, and observability in one FastAPI application.

Without explicit module boundaries, HTTP handling, PostgreSQL models, OpenAI SDK objects, and RAG logic could become tightly coupled. That would make pipeline stages difficult to test independently, compare experimentally, or replace later.

The first release is local and single-user. Ingestion runs synchronously, but its pipeline must remain independent of FastAPI so a different execution mechanism could be added without rewriting document-processing logic.

## Decision

The backend will use a modular monolith. Each module owns one business capability and exposes a small public interface to other modules.

The primary dependency direction is:

```text
API layer
    ↓
Application services and pipeline orchestration
    ↓
Domain models and interfaces
    ↓
Infrastructure adapters
```

Dependencies must not point upward. Infrastructure details are supplied to application services through interfaces and dependency injection.

## Module ownership

| Module | Owns | Does not own |
| --- | --- | --- |
| `api` | HTTP routes, request validation, response mapping, status codes, SSE framing | RAG decisions, SQL queries, provider logic |
| `core` | Settings, shared errors, identifiers, logging setup | Feature-specific business rules |
| `db` | SQLAlchemy session management, transaction helpers, shared persistence infrastructure | Document or conversation business behavior |
| `documents` | Document metadata, versions, statuses, upload lifecycle, deletion | Parsing and embedding algorithms |
| `ingestion` | Synchronous orchestration of document-processing stages | Parser, chunker, or embedding implementations |
| `parsing` | Source-format parsing and canonical element creation | Chunking, persistence, retrieval |
| `chunking` | Chunk creation, token limits, adjacency, and lineage | File parsing, embeddings, search |
| `embeddings` | Embedding interface, OpenAI adapter, batching, validation | Chunking and vector search |
| `retrieval` | Vector search, lexical search, fusion, candidate records | Reranking and answer generation |
| `reranking` | Reranker interface, candidate reordering, fallback result | Initial retrieval and context construction |
| `context` | Deduplication, adjacency expansion, token budgeting, source markers | Retrieval queries and model invocation |
| `generation` | Generation interface, OpenAI adapter, grounded response schema | Retrieval and citation metadata resolution |
| `citations` | Source-marker validation and deterministic metadata resolution | Generating citation identifiers with an LLM |
| `conversations` | Conversations, messages, history limits, query rewriting | Retrieval implementation |
| `evaluation` | Datasets, metrics, experiment execution, result persistence | Runtime API behavior |
| `observability` | OpenTelemetry instrumentation, trace attributes, SigNoz export | Business decisions and pipeline control flow |

## Public interfaces

Modules should expose behavior through application services or protocols rather than allowing other modules to import internal implementations.

Representative interfaces include:

```python
class DocumentParser(Protocol): ...
class ChunkingStrategy(Protocol): ...
class EmbeddingProvider(Protocol): ...
class Retriever(Protocol): ...
class Reranker(Protocol): ...
class GenerationProvider(Protocol): ...
class TelemetryRecorder(Protocol): ...
```

Provider-specific SDK types must be converted into internal types at the adapter boundary.

For example, the OpenAI embedding adapter returns an internal `EmbeddingBatch`, not an OpenAI SDK response. The generation adapter returns an internal grounded-answer model, not a provider response object.

## Shared types

Types should live with the module that owns their meaning.

Examples:

* `DocumentStatus` belongs to `documents`.
* `CanonicalElement` belongs to `parsing`.
* `Chunk` and `ChunkingConfig` belong to `chunking`.
* `RetrievalCandidate` belongs to `retrieval`.
* `AssembledContext` belongs to `context`.
* `GroundedAnswer` belongs to `generation`.
* `ResolvedCitation` belongs to `citations`.

A type may move to `core` only when it is genuinely feature-independent. `core` must not become a miscellaneous shared-code directory.

Separate representations are required at system boundaries:

```text
API request/response models
        ↕ explicit mapping
Application/domain models
        ↕ explicit mapping
Database models and provider responses
```

SQLAlchemy models must not be returned directly from API routes. Pydantic API models must not become the internal representation for every pipeline stage.

## Dependency rules

1. `api` may call application services but must not execute SQL or RAG stages directly.
2. `ingestion` may orchestrate parsing, chunking, embeddings, indexing, and document state transitions.
3. `parsing` must not depend on FastAPI, SQLAlchemy, OpenAI, retrieval, or generation.
4. `chunking` consumes canonical elements and must not read uploaded files.
5. `embeddings` must not decide how documents are chunked.
6. `retrieval` returns ranked evidence candidates and must not generate answers.
7. `reranking` accepts retrieval candidates and returns reordered candidates without mutating stored chunks.
8. `context` receives selected candidates and must not issue retrieval queries.
9. `generation` receives assembled evidence and must not access repositories or database models.
10. `citations` resolves only source markers that were assigned during context assembly.
11. `evaluation` may invoke public pipeline interfaces but must not duplicate runtime algorithms.
12. `observability` may wrap operations and record results but must not choose application behavior.
13. OpenAI SDK imports are permitted only inside OpenAI provider adapters and provider-specific configuration.
14. SigNoz-specific behavior must remain behind OpenTelemetry configuration or observability adapters.
15. Imports between sibling modules should target their public interfaces, not private implementation files.

## Transaction boundaries

Application services define transaction boundaries. Repositories participate in the caller's transaction and must not commit independently unless their interface explicitly represents an isolated operation.

For ingestion:

* Initial upload metadata may be committed before processing begins.
* Extracted elements, chunks, and embeddings are written for the processing version.
* The document becomes `READY` only after all required artifacts are valid.
* Activation is atomic.
* Failed or incomplete versions remain excluded from retrieval.

For deletion:

* The document first enters `DELETING`.
* Searchable artifacts and stored content are removed.
* A minimal tombstone may remain.
* The operation must be idempotent.

## Synchronous ingestion flow

```text
POST /documents
    │
    ▼
api.documents route
    │ validates HTTP input and maps the response
    ▼
documents.UploadDocumentService
    │ stores metadata and original file
    ▼
ingestion.SynchronousIngestionRunner
    ▼
ingestion.IngestionPipeline
    ├── parsing.DocumentParser
    ├── chunking.ChunkingStrategy
    ├── embeddings.EmbeddingProvider
    ├── persistence repositories
    └── documents document-state service
            │
            ▼
      atomic READY activation
```

The API route does not implement any ingestion stage. The synchronous runner is replaceable without changing `IngestionPipeline`.

## Query flow

```text
POST /chat
    │
    ▼
api.chat route
    │ validates input and opens SSE response
    ▼
conversations query service
    ├── load bounded conversation history
    └── rewrite follow-up query when required
    ▼
retrieval hybrid retriever
    ├── lexical retrieval
    ├── vector retrieval
    └── reciprocal rank fusion
    ▼
reranking reranker
    ▼
context context assembler
    ├── deduplicate and expand evidence
    ├── enforce token budget
    └── assign deterministic source markers
    ▼
generation OpenAI adapter
    ▼
citations validator and resolver
    ▼
api.chat route emits SSE events
```

The generation provider sees evidence text and source markers. It does not receive repositories or permission to invent document metadata.

## Observability boundary

Each application operation creates or extends an OpenTelemetry trace. Instrumentation may record:

* IDs and pipeline versions
* Stage durations and status
* Retrieval ranks and scores
* Model identifiers and token usage
* Estimated cost
* Errors and fallback decisions

Normal telemetry must not contain API keys, complete documents, or unrestricted context text. Observability failures must never cause the RAG request to fail.

## Enforcement

The boundaries will initially be enforced through:

* Code review
* Explicit module APIs
* Ruff linting and backend tests
* Unit tests around pure pipeline stages
* Integration tests at repository and provider boundaries
* Dependency injection from the application composition root

Automated import-boundary checks may be added if boundary violations become difficult to detect manually.

## Consequences

### Benefits

* Pipeline stages can be tested independently.
* OpenAI calls can be replaced with deterministic fakes.
* Retrieval experiments reuse production code.
* Synchronous ingestion is isolated from API routes, so the pipeline remains testable.
* Storage and observability providers can change behind adapters.
* Failures can be attributed to a specific stage.

### Costs

* Explicit mapping is required between API, domain, persistence, and provider models.
* Small interfaces and adapters add more code than directly calling dependencies.
* Developers must resist placing unrelated helpers in `core`.

These costs are accepted because inspectability, evaluation, and testability are primary project goals.

## Completion criteria

`FND-002` is complete when:

* Every backend module has a documented owner and responsibility.
* Dependency direction is explicit.
* Shared-type placement is defined.
* Provider SDK boundaries are defined.
* Synchronous ingestion and query flows are documented.
* Transaction and observability boundaries are documented.
* A developer can determine where new backend code belongs without guessing.
