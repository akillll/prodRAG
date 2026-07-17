# prodRAG Task Backlog

This backlog is intentionally scoped for a local, single-user, learning-first RAG system. The priority is to build and understand the core RAG pipeline end to end, then measure and improve it.

Out of scope for the first version:

* Durable job infrastructure
* Kubernetes
* Authentication and roles
* Multi-tenancy
* Object storage services
* Heavy frontend testing
* Enterprise administration features

---

# Phase 1: Foundation and First Working RAG

## Sprint 1: Project foundation

**Goal:** Create a clean local development foundation without unnecessary platform complexity.

- [ ☑️ ] `FND-001` Create frontend and backend project structure
  - **Description:** Establish the monorepo layout with separate frontend and backend folders.
- [ ☑️ ] `FND-002` Define backend module boundaries
  - **Description:** Document how ingestion, parsing, chunking, retrieval, generation, citations, and evaluation stay separated.
- [ ☑️ ] `FND-003` Configure backend test tooling
  - **Description:** Configure pytest and minimal backend project metadata so backend behavior can be tested as the RAG pipeline grows.
- [ ☑️ ] `FND-004` Configure TypeScript linting and type checking
  - **Description:** Add minimal frontend code-quality checks without adding frontend test frameworks.
- [ ☑️ ] `FND-005` Create minimal Docker Compose development stack
  - **Description:** Run only the local services needed for the app, starting with PostgreSQL and pgvector.
- [ ☑️ ] `FND-006` Configure PostgreSQL with pgvector
  - **Description:** Prepare the database for relational data, full-text search, and vector search.
- [ ☑️ ] `FND-007` Add environment configuration and `.env.example`
  - **Description:** Document required settings such as database URL, OpenAI API key, and model names.
- [ ☑️ ] `FND-008` Add database migration framework
  - **Description:** Add Alembic so schema changes are explicit and reproducible.
- [ ☑️ ] `FND-009` Add basic health endpoint
  - **Description:** Provide a simple API check for local development and troubleshooting.
- [ ☑️ ] `FND-010` Document local setup and common commands
  - **Description:** Make the project runnable from a clean checkout.

**Sprint gate:** A clean checkout can start the frontend, backend, and PostgreSQL locally, and backend/frontend quality checks run successfully.

---

## Sprint 2: Document ingestion and storage

**Goal:** Upload one document, validate it, store it locally, and track its processing state.

- [ ☑️ ] `ING-001` Design document, element, chunk, and version schemas
  - **Description:** Model the data needed for lineage, citations, deletion, and reprocessing.
- [ ☑️ ] `ING-002` Define document status lifecycle
  - **Description:** Use simple states such as `PROCESSING`, `READY`, `FAILED`, and `DELETING`.
- [ ☑️ ] `ING-003` Create ingestion-related migrations
  - **Description:** Create database tables for documents, versions, elements, chunks, and processing metadata.
- [ ☑️ ] `ING-004` Implement single-file upload API
  - **Description:** Accept one PDF, Markdown, or TXT file per request.
- [ ] `ING-005` Validate file type, size, and empty files
  - **Description:** Reject unsupported, oversized, corrupt, or empty files with clear errors.
- [ ☑️ ] `ING-006` Sanitize uploaded filenames
  - **Description:** Store files safely without trusting user-provided names.
- [ ☑️ ] `ING-007` Store original documents on the local filesystem
  - **Description:** Keep original files available for parsing, debugging, and reprocessing.
- [ ] `ING-008` Calculate content hashes
  - **Description:** Detect duplicate uploads and support idempotent processing.
- [ ] `ING-009` Implement document-list and status APIs
  - **Description:** Let the frontend show uploaded documents and their current state.
- [ ] `UI-001` Build basic document upload screen
  - **Description:** Provide a minimal UI for uploading a document and seeing validation errors.
- [ ] `UI-002` Build document status display
  - **Description:** Show whether a document is processing, ready, failed, or deleted.
- [ ] `TST-001` Test upload validation and duplicate detection
  - **Description:** Verify the important ingestion rules with deterministic backend tests.

**Sprint gate:** Users can upload one supported document, see its status, and avoid duplicate active documents.

---

## Sprint 3: Parsing and chunking

**Goal:** Convert documents into deterministic chunks with traceable lineage.

- [ ] `PAR-001` Define canonical parser interface
  - **Description:** Ensure all file types produce the same internal element model.
- [ ] `PAR-002` Implement TXT parser
  - **Description:** Parse plain text into ordered canonical elements.
- [ ] `PAR-003` Implement Markdown parser
  - **Description:** Preserve headings, paragraphs, lists, and code blocks.
- [ ] `PAR-004` Implement basic PDF parser
  - **Description:** Extract ordered text with page numbers where available.
- [ ] `PAR-005` Persist canonical elements
  - **Description:** Store parsed elements before chunking so parsing is inspectable.
- [ ] `CHK-001` Define chunker interface and configuration
  - **Description:** Make chunking strategies replaceable and measurable.
- [ ] `CHK-002` Implement heading-aware chunking
  - **Description:** Use document structure as the default chunking strategy.
- [ ] `CHK-003` Implement fixed-token baseline chunking
  - **Description:** Provide a simple baseline for later evaluation comparisons.
- [ ] `CHK-004` Preserve chunk lineage
  - **Description:** Store page, section path, source offsets where available, and previous/next chunk links.
- [ ] `CHK-005` Add token-limit and overlap handling
  - **Description:** Keep chunks within model limits while preserving useful context.
- [ ] `TST-002` Test deterministic parsing and chunking
  - **Description:** Confirm identical inputs and configs produce identical elements and chunks.

**Sprint gate:** The same document and configuration always produce the same elements, chunks, and lineage.

---

## Sprint 4: Embeddings, retrieval, and cited answers

**Goal:** Complete the first end-to-end RAG vertical slice.

- [ ] `EMB-001` Define embedding-provider interface
  - **Description:** Keep OpenAI-specific embedding code isolated from the rest of the pipeline.
- [ ] `EMB-002` Implement OpenAI embedding provider
  - **Description:** Generate embeddings through the commercial OpenAI API.
- [ ] `EMB-003` Add batched embedding requests
  - **Description:** Embed chunks efficiently while keeping implementation understandable.
- [ ] `EMB-004` Store embedding model and dimension metadata
  - **Description:** Make embedding outputs traceable and safe to compare later.
- [ ] `IDX-001` Store vectors in pgvector
  - **Description:** Persist chunk vectors for similarity search.
- [ ] `IDX-002` Add PostgreSQL full-text index
  - **Description:** Persist searchable text for lexical retrieval.
- [ ] `RET-001` Implement vector retrieval
  - **Description:** Retrieve candidate chunks using vector similarity.
- [ ] `CTX-001` Implement token-budgeted context assembly
  - **Description:** Select retrieved chunks and assign stable source markers.
- [ ] `GEN-001` Define generation-provider interface
  - **Description:** Isolate OpenAI generation code behind an internal interface.
- [ ] `GEN-002` Implement grounded answer generation
  - **Description:** Generate answers only from supplied evidence.
- [ ] `CIT-001` Resolve citation markers server-side
  - **Description:** Map model citation markers back to stored chunks.
- [ ] `CIT-002` Validate citations against supplied context
  - **Description:** Reject or repair citations that do not map to provided evidence.
- [ ] `API-001` Implement streaming chat endpoint with SSE
  - **Description:** Stream answer tokens/events to the frontend.
- [ ] `UI-003` Build minimal streaming chat screen
  - **Description:** Let users ask questions and see streamed answers.
- [ ] `UI-004` Build citation passage preview
  - **Description:** Let users inspect the exact evidence behind an answer.
- [ ] `TST-003` Test upload-to-cited-answer workflow
  - **Description:** Verify the full backend flow from document upload to cited answer.

**Phase 1 gate:** A user can upload one document and receive a streaming answer with valid, inspectable citations.

---

# Phase 2: Retrieval Quality and Transparency

## Sprint 5: Hybrid retrieval and reranking

**Goal:** Improve retrieval quality with a small set of measurable techniques.

- [ ] `RET-002` Implement full-text retrieval
  - **Description:** Retrieve candidates using PostgreSQL lexical search.
- [ ] `RET-003` Implement reciprocal rank fusion
  - **Description:** Combine vector and lexical results into one ranked list.
- [ ] `RET-004` Add vector-only, full-text-only, and hybrid modes
  - **Description:** Make retrieval modes easy to compare.
- [ ] `RET-005` Record retrieval scores and latency
  - **Description:** Capture enough data to understand why a result was selected.
- [ ] `RNK-001` Define reranker interface
  - **Description:** Keep reranking optional and replaceable.
- [ ] `RNK-002` Implement OpenAI or API-based reranking approach
  - **Description:** Improve candidate ordering without introducing local model infrastructure.
- [ ] `RNK-003` Add reranker timeout and fallback
  - **Description:** Fall back to fused results if reranking fails or is too slow.
- [ ] `CTX-002` Remove duplicate selected chunks
  - **Description:** Avoid wasting context window on repeated evidence.
- [ ] `CTX-003` Merge useful adjacent chunks
  - **Description:** Improve answer grounding when neighboring chunks complete the evidence.
- [ ] `TST-004` Test retrieval modes and reranker fallback
  - **Description:** Verify retrieval behavior and safe fallback paths.

**Sprint gate:** The same query can run in vector, full-text, hybrid, and reranked modes with comparable scores and timings.

---

## Sprint 6: Conversations, abstention, and retrieval debugger

**Goal:** Make answers more reliable and make RAG decisions inspectable.

- [ ] `CON-001` Create conversation and message schemas
  - **Description:** Store chat history without implementing long-term memory.
- [ ] `CON-002` Implement conversation APIs
  - **Description:** Create, list, read, and delete local conversations.
- [ ] `CON-003` Implement follow-up query rewriting
  - **Description:** Rewrite follow-up questions into standalone retrieval queries.
- [ ] `CON-004` Preserve original and rewritten queries
  - **Description:** Make query rewriting inspectable.
- [ ] `ABS-001` Define insufficient-evidence response contract
  - **Description:** Standardize how the system refuses unsupported answers.
- [ ] `ABS-002` Add no-evidence abstention
  - **Description:** Avoid answering when retrieval finds no useful evidence.
- [ ] `ABS-003` Add unsupported-answer abstention
  - **Description:** Avoid returning answers that cannot be tied to citations.
- [ ] `DBG-001` Create request-trace data model
  - **Description:** Store the key decisions made during retrieval and generation.
- [ ] `DBG-002` Capture retrieval candidates and final context
  - **Description:** Show what was retrieved, reranked, selected, and sent to the model.
- [ ] `DBG-003` Capture model, token, cost, and latency data
  - **Description:** Make quality, speed, and cost tradeoffs visible.
- [ ] `DBG-004` Implement trace-detail API
  - **Description:** Expose one trace in a structured format for the debugger UI.
- [ ] `UI-005` Build retrieval-debugger screen
  - **Description:** Let users inspect retrieval, context assembly, generation, and citations.
- [ ] `TST-005` Test abstention and trace creation
  - **Description:** Verify unsupported questions and trace persistence.

**Phase 2 gate:** A user can inspect how an answer was produced and see when the system refuses to answer.

---

# Phase 3: Evaluation and Experiments

## Sprint 7: Evaluation foundation

**Goal:** Build a small, versioned benchmark that measures retrieval and answer quality.

- [ ] `EVAL-001` Define evaluation-example schema
  - **Description:** Represent questions, expected evidence, expected answer notes, and answerability.
- [ ] `EVAL-002` Create licensed sample corpus
  - **Description:** Add documents that are safe to include in a public portfolio repo.
- [ ] `EVAL-003` Write exact-fact evaluation cases
  - **Description:** Test questions with clear supporting evidence.
- [ ] `EVAL-004` Write semantic evaluation cases
  - **Description:** Test questions where evidence uses different wording.
- [ ] `EVAL-005` Write unanswerable evaluation cases
  - **Description:** Test whether the system abstains correctly.
- [ ] `MET-001` Implement Recall@k and hit rate
  - **Description:** Measure whether retrieval finds the expected evidence.
- [ ] `MET-002` Implement MRR
  - **Description:** Measure how highly the expected evidence ranks.
- [ ] `MET-003` Record latency, token usage, and estimated cost
  - **Description:** Track practical tradeoffs alongside quality.
- [ ] `RUN-001` Implement retrieval evaluation runner
  - **Description:** Run the dataset against configured retrieval modes.
- [ ] `RUN-002` Persist evaluation results
  - **Description:** Save machine-readable results for later comparison.
- [ ] `TST-006` Test metric calculations with fixtures
  - **Description:** Verify metrics with known expected values.

**Sprint gate:** A clean checkout can run a small benchmark and reproduce retrieval metrics.

---

## Sprint 8: Experiments and portfolio polish

**Goal:** Turn the project into a portfolio-quality demonstration with measured claims.

- [ ] `EXP-001` Compare fixed-token and heading-aware chunking
  - **Description:** Show whether structure-aware chunking improves retrieval quality.
- [ ] `EXP-002` Compare vector, full-text, and hybrid retrieval
  - **Description:** Show when each retrieval mode succeeds or fails.
- [ ] `EXP-003` Compare hybrid retrieval with and without reranking
  - **Description:** Keep reranking only if measured value justifies its cost and latency.
- [ ] `REP-001` Generate evaluation result report
  - **Description:** Summarize quality, latency, and cost in a readable artifact.
- [ ] `UI-006` Build simple evaluation-results screen
  - **Description:** Display latest benchmark results without building a full analytics product.
- [ ] `OBS-001` Add structured JSON logs
  - **Description:** Make local debugging easier with request IDs, stage names, durations, and errors.
- [ ] `OBS-002` Add optional OpenTelemetry export to SigNoz
  - **Description:** Export traces/logs when configured, while keeping the app usable without SigNoz.
- [ ] `DOC-001` Create architecture diagram
  - **Description:** Explain the system at a glance.
- [ ] `DOC-002` Create ingestion and query sequence diagrams
  - **Description:** Show the two most important runtime flows.
- [ ] `DOC-003` Document data model and module boundaries
  - **Description:** Make design decisions understandable to reviewers.
- [ ] `DOC-004` Document evaluation methodology and results
  - **Description:** Support portfolio claims with reproducible evidence.
- [ ] `DOC-005` Complete clean-checkout README walkthrough
  - **Description:** Ensure another developer can run the project.
- [ ] `DEMO-001` Prepare demo dataset
  - **Description:** Provide a reliable demo path using redistributable documents.
- [ ] `DEMO-002` Record short demonstration video
  - **Description:** Show ingestion, cited answers, abstention, debugger, and evaluation.

**Phase 3 gate:** The project has a working RAG demo, inspectable decisions, and benchmark-backed claims.

---

# Final Release Checklist

## Functional

- [ ] Single-file PDF, Markdown, and TXT upload works
- [ ] Parsing and chunking preserve enough structure for citations
- [ ] Vector, full-text, hybrid, and reranked retrieval work
- [ ] Streaming answers contain deterministic, valid citations
- [ ] Citation previews expose the supporting evidence
- [ ] Follow-up questions use traceable query rewriting
- [ ] Unsupported questions produce abstention responses
- [ ] Retrieval traces are inspectable in the debugger
- [ ] Evaluation runs and experiment comparisons are reproducible

## Quality

- [ ] Failed and incomplete documents never appear in retrieval
- [ ] Deleted documents never appear in subsequent retrieval
- [ ] Every citation maps to evidence supplied to the model
- [ ] Reranking is retained only with documented measured benefit
- [ ] Backend unit, integration, and workflow tests pass
- [ ] Formatting, linting, frontend TypeScript checks, and backend tests pass

## Portfolio

- [ ] Clean local setup is documented and verified
- [ ] Architecture and sequence diagrams are complete
- [ ] Benchmark results include quality, latency, and cost
- [ ] Engineering decisions and tradeoffs are documented
- [ ] Known limitations are explicit
- [ ] Sample corpus and evaluation dataset have valid redistribution rights
- [ ] Demo video shows ingestion, citations, abstention, debugging, and evaluation

---

# Task ID Legend

| Prefix | Meaning | Scope |
| --- | --- | --- |
| `ABS` | Abstention | Insufficient-evidence and non-answer behavior |
| `API` | Application Programming Interface | Backend endpoints and streaming API behavior |
| `CHK` | Chunking | Chunk creation, configuration, and lineage |
| `CIT` | Citations | Source-marker validation and citation resolution |
| `CON` | Conversations | Conversation storage, history, and query rewriting |
| `CTX` | Context Assembly | Evidence selection, token budgeting, and source markers |
| `DBG` | Debugger | Retrieval traces and debugger interface |
| `DEMO` | Demonstration | Demo dataset and portfolio video |
| `DOC` | Documentation | Architecture, setup, decisions, and benchmarks |
| `EMB` | Embeddings | Embedding providers, batching, validation, and metadata |
| `EVAL` | Evaluation Dataset | Evaluation schema, cases, corpus, and versioning |
| `EXP` | Experiments | Controlled retrieval and chunking comparisons |
| `FND` | Foundation | Project structure, infrastructure, and standards |
| `GEN` | Generation | Grounded LLM answer generation |
| `IDX` | Indexing | Vector and search index operations |
| `ING` | Ingestion | Upload, validation, storage, status, and processing |
| `MET` | Metrics | Retrieval, answer, citation, and cost measurements |
| `OBS` | Observability | Structured logs, traces, and operational visibility |
| `PAR` | Parsing | Source parsing and canonical element extraction |
| `REP` | Reporting | Evaluation reports and result interfaces |
| `RET` | Retrieval | Lexical, vector, hybrid, and fused search |
| `RNK` | Reranking | Optional reranking and fallback behavior |
| `RUN` | Evaluation Runner | Evaluation execution and result persistence |
| `TST` | Testing | Backend unit, integration, workflow, and failure tests |
| `UI` | User Interface | Document, chat, citation, debugger, and evaluation screens |
