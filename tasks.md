# Phase 1: Foundation and Vertical Slice

## Sprint 1: Project foundation

**Goal:** Start the complete local stack and establish engineering standards.

- [ ] `FND-001` Create frontend and backend project structure
- [ ] `FND-002` Define backend module boundaries
- [ ] `FND-003` Configure Python formatting, linting, and type checking
- [ ] `FND-004` Configure TypeScript formatting, linting, and type checking
- [ ] `FND-005` Create Docker Compose development stack
- [ ] `FND-006` Configure PostgreSQL with pgvector
- [ ] `FND-007` Configure Redis and background worker
- [ ] `FND-008` Configure object-storage abstraction
- [ ] `FND-009` Add environment configuration and `.env.example`
- [ ] `FND-010` Add database migration framework
- [ ] `FND-011` Add health and readiness endpoints
- [ ] `FND-012` Add structured API error format
- [ ] `FND-013` Create initial CI workflow
- [ ] `FND-014` Document local setup and common commands

**Sprint gate:** A clean checkout starts all services, passes lint and type checks, and exposes healthy frontend, API, worker, database, Redis, and storage services.

---

## Sprint 2: Document model and upload

**Goal:** Accept documents safely and track their lifecycle.

- [ ] `ING-001` Design document, version, element, chunk, and job schemas
- [ ] `ING-002` Create document-status state machine
- [ ] `ING-003` Add document and processing-job migrations
- [ ] `ING-004` Implement single-file upload API
- [ ] `ING-006` Validate extension, MIME type, size, and empty files
- [ ] `ING-007` Sanitize uploaded filenames
- [ ] `ING-008` Store original documents
- [ ] `ING-009` Calculate content hashes
- [ ] `ING-010` Detect duplicate content
- [ ] `ING-011` Queue document-processing jobs
- [ ] `ING-012` Implement document-list and status APIs
- [ ] `ING-013` Build basic document upload screen
- [ ] `ING-014` Build document status and error display
- [ ] `ING-015` Test upload validation and duplicate handling

**Sprint gate:** Users can upload PDF, Markdown, and TXT files and see each document enter the processing queue exactly once.

---

## Sprint 3: Parsing and chunking

**Goal:** Convert supported documents into deterministic, traceable chunks.

- [ ] `PAR-001` Define canonical parser interface
- [ ] `PAR-002` Implement TXT parser
- [ ] `PAR-003` Implement Markdown structure-aware parser
- [ ] `PAR-004` Implement PDF structure-aware parser
- [ ] `PAR-005` Preserve page numbers and source order
- [ ] `PAR-006` Preserve headings, paragraphs, lists, and code blocks
- [ ] `PAR-007` Persist canonical elements and section hierarchy
- [ ] `CHK-001` Define chunker interface and configuration
- [ ] `CHK-002` Implement heading-aware chunking
- [ ] `CHK-003` Implement small-section merging
- [ ] `CHK-004` Implement oversized-section splitting
- [ ] `CHK-005` Add overlap and token-limit handling
- [ ] `CHK-006` Persist chunk lineage and adjacency
- [ ] `CHK-007` Version parser and chunking configurations
- [ ] `CHK-008` Test deterministic chunk output
- [ ] `CHK-009` Test lineage, page, section, and offset preservation

**Sprint gate:** The same document and configuration always produce the same structured elements, chunks, and lineage.

---

## Sprint 4: Embeddings and cited answers

**Goal:** Complete the first end-to-end RAG vertical slice.

- [ ] `EMB-001` Define embedding-provider interface
- [ ] `EMB-002` Implement initial embedding provider
- [ ] `EMB-003` Add batched embedding requests
- [ ] `EMB-004` Validate token limits and vector dimensions
- [ ] `EMB-005` Add embedding retry and rate-limit handling
- [ ] `EMB-006` Persist embedding model and version metadata
- [ ] `IDX-001` Index chunk vectors in pgvector
- [ ] `IDX-002` Filter retrieval to ready documents
- [ ] `RET-001` Implement vector similarity retrieval
- [ ] `CTX-001` Implement basic token-budgeted context assembly
- [ ] `CTX-002` Assign deterministic source markers
- [ ] `GEN-001` Define generation-provider interface
- [ ] `GEN-002` Implement grounded structured generation
- [ ] `CIT-001` Resolve source markers server-side
- [ ] `CIT-002` Validate citation markers against supplied context
- [ ] `API-001` Implement streaming chat endpoint
- [ ] `UI-001` Build minimal streaming chat screen
- [ ] `UI-002` Build citation passage preview
- [ ] `TST-001` Add API workflow test for upload-to-cited-answer

**Phase 1 gate:** A new user can start the system, upload a document, and receive a streaming answer with valid, inspectable citations.

---

# Phase 2: Retrieval Quality

## Sprint 5: Hybrid retrieval

**Goal:** Add lexical retrieval and a measurable hybrid-search pipeline.

- [ ] `RET-002` Implement PostgreSQL full-text indexing
- [ ] `RET-003` Implement full-text retrieval
- [ ] `RET-004` Implement reciprocal rank fusion
- [ ] `RET-005` Add configurable retrieval candidate counts
- [ ] `RET-006` Deduplicate fused results
- [ ] `RET-007` Record source ranks, scores, and latency
- [ ] `RET-008` Add vector-only retrieval mode
- [ ] `RET-009` Add full-text-only retrieval mode
- [ ] `RET-010` Add hybrid retrieval mode
- [ ] `RET-011` Test ready-document filtering
- [ ] `RET-012` Test deterministic rank fusion
- [ ] `DBG-001` Expose retrieval results through debug API

**Sprint gate:** The same query can run in full-text, vector, or hybrid mode, with ranks and scores available for comparison.

---

## Sprint 6: Reranking and context assembly

**Goal:** Improve evidence selection while preserving bounded latency and context size.

- [ ] `RNK-001` Define reranker interface
- [ ] `RNK-002` Implement cross-encoder reranker
- [ ] `RNK-003` Add candidate and final-result configuration
- [ ] `RNK-004` Record reranking scores and latency
- [ ] `RNK-005` Add reranker timeout
- [ ] `RNK-006` Fall back to fused order on failure
- [ ] `CTX-003` Remove exact duplicate chunks
- [ ] `CTX-004` Remove near-duplicate chunks
- [ ] `CTX-005` Merge useful adjacent chunks
- [ ] `CTX-006` Expand parent sections when useful
- [ ] `CTX-007` Preserve source diversity
- [ ] `CTX-008` Enforce exact context token budgets
- [ ] `CTX-009` Store protected context snapshots
- [ ] `TST-002` Test reranker failure fallback
- [ ] `TST-003` Test context budget and source-marker stability

**Sprint gate:** Reranking and context assembly are bounded, traceable, and safe when the reranker is unavailable.

---

## Sprint 7: Conversations and abstention

**Goal:** Support reliable follow-up questions and honest non-answers.

- [ ] `CON-001` Create conversation and message schemas
- [ ] `CON-002` Implement conversation CRUD APIs
- [ ] `CON-003` Persist chat messages
- [ ] `CON-004` Enforce conversation-history token limits
- [ ] `CON-005` Implement follow-up query rewriting
- [ ] `CON-006` Preserve original and rewritten queries
- [ ] `ABS-001` Define insufficient-evidence response contract
- [ ] `ABS-002` Add no-evidence abstention
- [ ] `ABS-003` Add unsupported-evidence abstention
- [ ] `ABS-004` Add conflicting-evidence handling
- [ ] `ABS-005` Abstain on invalid citations
- [ ] `SEC-001` Add query and output-token limits
- [ ] `SEC-002` Add query rate limiting
- [ ] `SEC-003` Harden prompts against document instructions
- [ ] `UI-003` Add conversation history and deletion
- [ ] `UI-004` Add new-conversation and stop-generation actions
- [ ] `UI-005` Add insufficient-evidence state
- [ ] `TST-004` Test follow-up rewriting and history limits
- [ ] `TST-005` Test prompt-injection documents

**Sprint gate:** Follow-up questions resolve correctly, while unsupported or conflicting questions return a consistent abstention response.

---

## Sprint 8: Retrieval debugger

**Goal:** Make every RAG decision inspectable from the application.

- [ ] `DBG-002` Create request-trace data model
- [ ] `DBG-003` Capture original and rewritten queries
- [ ] `DBG-004` Capture lexical and vector results
- [ ] `DBG-005` Capture fusion and reranking results
- [ ] `DBG-006` Capture selected chunks and final context
- [ ] `DBG-007` Capture prompts, models, and token usage
- [ ] `DBG-008` Capture citation mappings
- [ ] `DBG-009` Capture stage timings and fallbacks
- [ ] `DBG-010` Implement trace-detail API
- [ ] `DBG-011` Build retrieval-debugger screen
- [ ] `DBG-012` Visualize retrieval-stage progression
- [ ] `DBG-013` Display scores, latency, tokens, and cost
- [ ] `DBG-014` Protect context snapshots from normal logs
- [ ] `TST-006` Test complete trace creation

**Phase 2 gate:** Every retrieval and generation stage is inspectable, and full-text, vector, hybrid, and reranked results can be compared.

---

# Phase 3: Evaluation and Experimentation

## Sprint 9: Evaluation foundation

**Goal:** Create a versioned benchmark and reproducible retrieval evaluation.

- [ ] `EVAL-001` Define evaluation-example schema
- [ ] `EVAL-002` Define dataset validation rules
- [ ] `EVAL-003` Create licensed sample document corpus
- [ ] `EVAL-004` Write exact-fact evaluation cases
- [ ] `EVAL-005` Write semantic evaluation cases
- [ ] `EVAL-006` Write multi-section and multi-document cases
- [ ] `EVAL-007` Write follow-up evaluation cases
- [ ] `EVAL-008` Write unanswerable and conflicting-source cases
- [ ] `EVAL-009` Write prompt-injection cases
- [ ] `EVAL-010` Version the initial evaluation dataset
- [ ] `MET-001` Implement Recall@k
- [ ] `MET-002` Implement Precision@k and hit rate
- [ ] `MET-003` Implement MRR and NDCG@k
- [ ] `MET-004` Record retrieval latency
- [ ] `RUN-001` Implement retrieval evaluation runner
- [ ] `TST-007` Test metric calculations with known fixtures

**Sprint gate:** A clean checkout can run a versioned dataset and reproduce retrieval metrics for every retrieval mode.

---

## Sprint 10: Answer evaluation and experiments

**Goal:** Measure answer quality and make configuration choices from evidence.

- [ ] `MET-005` Implement answer-correctness evaluation
- [ ] `MET-006` Implement faithfulness evaluation
- [ ] `MET-007` Implement citation-correctness evaluation
- [ ] `MET-008` Implement citation-completeness evaluation
- [ ] `MET-009` Implement unsupported-claim measurement
- [ ] `MET-010` Implement invalid-citation measurement
- [ ] `MET-011` Implement abstention-accuracy measurement
- [ ] `MET-012` Record latency, token usage, and cost
- [ ] `RUN-002` Persist evaluation-run configuration
- [ ] `RUN-003` Persist per-example results and failures
- [ ] `EXP-001` Implement fixed-token baseline chunker
- [ ] `EXP-002` Compare fixed and heading-aware chunking
- [ ] `EXP-003` Compare lexical, vector, and hybrid retrieval
- [ ] `EXP-004` Compare hybrid retrieval with and without reranking
- [ ] `EXP-005` Compare selected chunk sizes
- [ ] `EXP-006` Compare selected candidate counts
- [ ] `REP-001` Generate machine-readable result reports
- [ ] `REP-002` Build evaluation-results screen
- [ ] `REP-003` Build individual-failure inspection view
- [ ] `CI-001` Add evaluation regression checks to CI

**Phase 3 gate:** Quality claims and chosen defaults are backed by reproducible quality, latency, and cost comparisons.

---

# Phase 4: Reliability and Portfolio Polish

## Sprint 11: Reliability and observability

**Goal:** Make failure, retry, deletion, and dependency behavior trustworthy.

- [ ] `REL-001` Add stage-specific ingestion retries
- [ ] `REL-002` Add maximum retry and terminal-failure handling
- [ ] `REL-003` Add safe partial-artifact cleanup
- [ ] `REL-004` Guarantee atomic document activation
- [ ] `REL-005` Implement idempotent reprocessing
- [ ] `REL-006` Implement complete document deletion
- [ ] `REL-007` Add deletion tombstones and audit events
- [ ] `REL-008` Detect missing embeddings
- [ ] `REL-009` Detect stale and orphaned index entries
- [ ] `REL-010` Add index-health reporting
- [ ] `OBS-001` Add request and trace IDs
- [ ] `OBS-002` Add OpenTelemetry query tracing
- [ ] `OBS-003` Add ingestion-job tracing
- [ ] `OBS-004` Add structured application logs
- [ ] `OBS-005` Add external-service timeouts
- [ ] `OBS-006` Add graceful provider-failure responses
- [ ] `OBS-007` Redact secrets and document content from logs
- [ ] `TST-008` Test failed-ingestion isolation
- [ ] `TST-009` Test idempotent retries and reprocessing
- [ ] `TST-010` Test complete deletion from all indexes

**Sprint gate:** Failure injection confirms that partial documents remain hidden, retries are idempotent, and deletion removes all searchable artifacts.

---

## Sprint 12: Portfolio release

**Goal:** Produce a polished, reproducible public project.

- [ ] `UI-006` Polish loading, empty, success, and error states
- [ ] `UI-007` Polish document-management flow
- [ ] `UI-008` Polish chat, citation, and debugger experiences
- [ ] `UI-009` Add incorrect-citation feedback action
- [ ] `PERF-001` Measure ingestion throughput
- [ ] `PERF-002` Measure retrieval and generation latency
- [ ] `PERF-003` Measure token usage and estimated cost
- [ ] `PERF-004` Document performance bottlenecks
- [ ] `DOC-001` Create system architecture diagram
- [ ] `DOC-002` Create ingestion sequence diagram
- [ ] `DOC-003` Create query sequence diagram
- [ ] `DOC-004` Document data model and module boundaries
- [ ] `DOC-005` Document configuration and provider setup
- [ ] `DOC-006` Document security model and limitations
- [ ] `DOC-007` Document chosen defaults and tradeoffs
- [ ] `DOC-008` Publish benchmark methodology and results
- [ ] `DOC-009` Publish known limitations and future work
- [ ] `DOC-010` Complete clean-checkout README walkthrough
- [ ] `TST-011` Complete backend workflow happy-path suite
- [ ] `TST-012` Complete critical failure-path suite
- [ ] `REL-011` Verify one-command local startup
- [ ] `REL-012` Create tagged release
- [ ] `DEMO-001` Prepare demo dataset
- [ ] `DEMO-002` Record short demonstration video

**Phase 4 gate:** Another developer can clone, configure, run, test, evaluate, and understand the system without private instructions.

---

# Final Release Checklist

## Functional

- [ ] Upload, processing, retry, reprocessing, and deletion work
- [ ] PDF, Markdown, and TXT parsing preserve required structure
- [ ] Full-text, vector, hybrid, and reranked retrieval work
- [ ] Streaming answers contain deterministic, valid citations
- [ ] Citation previews expose the supporting evidence
- [ ] Follow-up questions use traceable query rewriting
- [ ] Unsupported questions produce abstention responses
- [ ] Retrieval traces are inspectable in the debugger
- [ ] Evaluation runs and experiment comparisons are reproducible

## Quality

- [ ] Citation correctness is at least 95% on the curated dataset
- [ ] Invalid-citation rate is zero
- [ ] Abstention accuracy is at least 90% on the curated dataset
- [ ] Reranking is retained only with documented measured benefit
- [ ] Failed and incomplete documents never appear in retrieval
- [ ] Deleted documents never appear in subsequent retrieval
- [ ] Critical backend unit, integration, and workflow tests pass
- [ ] Linting, formatting, type checking, tests, and regression checks pass in CI

## Portfolio

- [ ] One-command startup is documented and verified
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
| `CI` | Continuous Integration | Automated quality and evaluation checks |
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
| `ING` | Ingestion | Upload, validation, storage, status, and jobs |
| `MET` | Metrics | Retrieval, answer, citation, and abstention measurements |
| `OBS` | Observability | Tracing, structured logs, and operational visibility |
| `PAR` | Parsing | Source parsing and canonical element extraction |
| `PERF` | Performance | Throughput, latency, token, and cost measurements |
| `REL` | Reliability | Retry, cleanup, deletion, idempotency, and health |
| `REP` | Reporting | Evaluation reports and result interfaces |
| `RET` | Retrieval | Lexical, vector, hybrid, and fused search |
| `RNK` | Reranking | Cross-encoder reranking and fallback behavior |
| `RUN` | Evaluation Runner | Evaluation execution and result persistence |
| `SEC` | Security | RAG-focused limits and injection protections |
| `TST` | Testing | Backend unit, integration, workflow, regression, and failure tests |
| `UI` | User Interface | Document, chat, citation, and debugger experiences |
