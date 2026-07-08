# Evaluation-Driven RAG System Scope

## 1. Product goal

Build a complete, high-quality RAG system that demonstrates strong understanding of:

* Document ingestion and normalization
* Chunking and document lineage
* Embeddings and indexing
* Hybrid retrieval and reranking
* Evidence-grounded answer generation
* Deterministic citations
* Evaluation and experimentation
* Debuggability and practical engineering quality

The application is a focused document knowledge assistant, not an enterprise administration platform.

The key portfolio claim is:

> An evaluation-driven RAG system that makes retrieval decisions inspectable and measures how chunking, hybrid search, and reranking affect answer quality.

---

## 2. User experience

A user can:

* Upload supported documents
* Monitor document-processing status
* Retry failed processing
* Delete documents
* Ask questions about ready documents
* Receive streaming, evidence-grounded answers
* Inspect citations and source passages
* Receive an explicit insufficient-evidence response
* Continue a conversation with follow-up questions
* Inspect how retrieval produced an answer
* View evaluation and experiment results

The first release is a local or single-user application. Authentication, roles, multi-tenancy, billing, and enterprise administration are not required.

---

# Must Have

## 3. Document ingestion

Initially support:

* PDF
* Markdown
* TXT

Required capabilities:

* Single-file upload
* File-extension and MIME-type validation
* Configurable maximum file size
* Empty-file detection
* Corrupt-file handling
* Filename sanitization
* Content-hash duplicate detection
* Processing-status display
* Failure reason
* Retry failed processing
* Idempotent reprocessing
* Document deletion

Document statuses:

```text
PROCESSING
READY
FAILED
DELETING
```

Only `READY` documents are searchable.

---

## 4. Synchronous processing pipeline

Document processing runs synchronously in the first version:

```text
Upload
→ Validate
→ Store original
→ Parse
→ Normalize
→ Chunk
→ Embed
→ Index
→ Activate
```

Required behavior:

* Stage-level status and timings
* Manual retry for failed processing
* Clear failure reason
* Processing-version identifier
* Idempotent stages
* Safe cleanup after failure
* Atomic activation after all processing succeeds
* Incomplete document versions are never searchable

This project intentionally does not use durable job infrastructure in the first version. The ingestion pipeline should still be written as a separate service/module so its execution mechanism can change later if the project scope changes.

Document deletion must remove:

* Original file
* Extracted elements
* Chunks
* Embeddings
* Full-text index entries
* Cached retrieval results

A minimal deletion tombstone and audit event may remain, but deleted content must not remain searchable.

---

## 5. Canonical document model

Every parser converts source content into a shared internal structure:

```text
Document
└── Section
    └── Element
        └── Chunk
```

Supported element types:

* Title
* Heading
* Paragraph
* List
* Code block

Each element should retain:

* Element ID
* Document ID
* Document version ID
* Element type
* Content
* Page number where available
* Section path
* Parent element ID
* Element order
* Text offsets where available
* Token count
* Metadata

Each chunk should retain:

* Chunk ID
* Document and version IDs
* Source filename
* Page number
* Section path
* Parent section ID
* Previous and next chunk IDs
* Original text offsets where available
* Chunking strategy and configuration
* Parser and processing versions

This lineage is required for citations, debugging, deletion, and reprocessing.

---

## 6. Structure-aware parsing

Parsing should preserve:

* Document title
* Heading hierarchy
* Paragraph and list boundaries
* Code blocks
* Page numbers where available
* Source order

Documents must not be reduced to one unstructured text string.

Scanned-document OCR, image understanding, and advanced table extraction are not required for the first release.

---

## 7. Chunking

Implement two strategies:

1. Fixed-token chunking as an experimental baseline
2. Heading-aware chunking as the production default

Required capabilities:

* Configurable chunk size
* Configurable overlap
* Minimum chunk size
* Small-section merging
* Oversized-section splitting
* Heading inclusion
* Parent-section reference
* Token-count validation
* Deterministic output for identical input and configuration

The evaluation framework must compare both strategies instead of adding more strategies without measured value.

---

## 8. Embedding pipeline

Required capabilities:

* Batched embedding
* Token-limit validation
* Transient-error retry
* Rate-limit handling
* Dimension validation
* Model name and version tracking
* Processing timestamps
* Re-embedding support
* Removal of obsolete embeddings
* Replaceable embedding-provider interface

Provider-specific code must not leak into chunking, retrieval, or evaluation modules.

---

## 9. Storage and indexes

Maintain both:

```text
Full-text index
      +
Vector index
```

The recommended first implementation is PostgreSQL with:

* Relational tables for document metadata and lineage
* PostgreSQL full-text search for lexical retrieval
* pgvector for vector retrieval

Required index operations:

* Add document chunks
* Replace document chunks during reprocessing
* Delete every artifact belonging to a document
* Filter out non-ready documents
* Detect missing embeddings
* Detect stale or orphaned index entries
* Report index-health failures

---

## 10. Hybrid retrieval

Retrieval pipeline:

```text
Vector search ───┐
                 ├─ Reciprocal Rank Fusion → Reranking
Full-text search ┘
```

Required capabilities:

* Vector similarity retrieval
* Full-text/BM25-style retrieval
* Reciprocal rank fusion
* Configurable candidate counts
* Ready-document filtering
* Exact-score and rank recording
* Duplicate-result removal
* Retrieval latency tracking

Hybrid retrieval must be compared against vector-only and full-text-only baselines.

---

## 11. Reranking

Retrieve a broad candidate set, then rerank it:

```text
Hybrid retrieval: top 30–50
→ Cross-encoder reranker
→ Final top 5–10
```

Required capabilities:

* Configurable candidate and final-result counts
* Reranking score storage
* Reranking latency tracking
* Timeout
* Fallback to fused retrieval order
* Evaluation with and without reranking

Reranking remains enabled only if evaluation shows sufficient quality benefit for its latency and cost.

---

## 12. Context assembly

The context builder should:

* Remove duplicate and near-duplicate chunks
* Merge useful adjacent chunks
* Expand parent context when useful
* Preserve source diversity
* Order evidence by relevance
* Enforce an exact token budget
* Assign deterministic source markers such as `[S1]`
* Record the exact evidence supplied to generation

Exact context snapshots belong in a protected trace store with limited retention. Normal application logs should contain IDs and redacted metadata, not complete document contents.

---

## 13. Grounded answer generation

The generation model must:

* Answer only from supplied evidence
* Cite factual claims
* Separate supported facts from inference
* Mention conflicting evidence
* State meaningful limitations
* Abstain when evidence is insufficient
* Treat document content as untrusted data
* Ignore instructions contained inside retrieved documents

Use schema-validated structured output:

```json
{
  "answer": "Employees receive 20 days of annual leave [S1].",
  "citations": ["S1"],
  "answerable": true,
  "limitations": []
}
```

The model may reference only source markers supplied in the context. The backend resolves source markers to document IDs, chunk IDs, page numbers, sections, and passages.

---

## 14. Citation system

Every resolved citation should contain:

* Source marker
* Document ID and name
* Document version
* Chunk ID
* Page number where available
* Section path
* Supporting passage
* Surrounding context

Users should be able to:

* Click citation markers
* Preview the supporting passage
* See the document, page, and section
* View surrounding source text
* Open the original document at the relevant page where possible
* Report an incorrect citation

The backend must reject or safely repair responses containing unknown citation markers. The model must never generate document IDs, chunk IDs, or page numbers directly.

---

## 15. Conversational questions

Support:

* Conversation ID
* Conversation history
* Follow-up query rewriting
* Configurable history token limit
* New conversation
* Conversation deletion

Both the original and rewritten query must be available in the retrieval debugger.

Long-term personalized memory and autonomous agent loops are not required.

---

## 16. Insufficient-evidence handling

The system should abstain when:

* No relevant evidence is retrieved
* Retrieved evidence does not answer the question
* Sources conflict without a supported resolution
* Required information is absent
* Citations cannot be validated

Example:

```text
The available documents do not contain enough evidence to answer this reliably.
```

Abstention thresholds must be tuned using evaluation data, not arbitrary similarity-score assumptions. The system must not invent confidence percentages.

---

## 17. Focused RAG security

The first release needs protections that directly affect RAG correctness:

* Query-length and output-token limits
* Upload validation
* Rate limiting
* Retrieved content treated as untrusted
* Prompt-injection instructions in documents ignored
* Only ready documents retrieved
* Citation-marker validation
* Secrets excluded from logs and repository
* Safe handling of model-provider failures
* Configurable timeouts for external calls

A full PII governance system, jailbreak classifier, policy engine, and security administration dashboard are outside the first-release scope.

---

## 18. Retrieval debugger

The retrieval debugger is a signature portfolio feature.

For each request, display:

* Request and trace IDs
* Original query
* Rewritten query
* Full-text results and scores
* Vector results and scores
* Fusion ranks
* Reranker scores
* Final selected chunks
* Context supplied to the model
* Context token count
* Prompt version
* Embedding, reranking, and generation models
* Generated structured response
* Resolved citation mapping
* Stage-level latency
* Input and output token usage
* Estimated request cost
* Errors and fallback decisions

The debugger must make each stage understandable without requiring access to server logs.

---

## 19. Evaluation dataset

Create a version-controlled evaluation dataset with manually reviewed examples.

Include:

* Exact-fact questions
* Semantic questions
* Multi-section questions
* Multi-document questions
* Follow-up questions
* Unanswerable questions
* Conflicting-source questions
* Prompt-injection documents and questions

Example:

```json
{
  "id": "cancellation-period-01",
  "question": "What is the cancellation period?",
  "reference_answer": "The cancellation period is 30 days.",
  "relevant_document_ids": ["document-12"],
  "relevant_chunk_ids": ["chunk-12"],
  "required_claims": ["The cancellation period is 30 days"],
  "answerable": true,
  "question_type": "fact"
}
```

The initial target is 100–200 carefully reviewed questions. Dataset quality is more important than raw size.

---

## 20. Retrieval evaluation

Measure:

* Recall@k
* Precision@k
* Hit rate
* Mean reciprocal rank
* NDCG@k
* Retrieval latency

Compare:

* Full-text retrieval
* Vector retrieval
* Hybrid retrieval
* Hybrid retrieval with reranking
* Fixed-token chunking
* Heading-aware chunking
* Selected chunk sizes and candidate counts

---

## 21. Answer evaluation

Measure:

* Answer correctness
* Faithfulness to supplied evidence
* Citation correctness
* Citation completeness
* Unsupported-claim rate
* Invalid-citation rate
* Abstention accuracy
* End-to-end latency
* Token usage
* Estimated cost

Every evaluation run must record:

* Dataset version
* Parser version
* Chunking strategy and configuration
* Embedding model
* Retrieval configuration
* Reranker
* Prompt version
* Generation model
* Code revision
* Execution timestamp

Evaluation output should be stored in a machine-readable format and displayed as a generated report or simple results dashboard.

---

## 22. Experiment tracking

Experiments must be reproducible and compare one meaningful change at a time.

Required comparisons:

* Fixed-token versus heading-aware chunking
* Full-text versus vector retrieval
* Vector versus hybrid retrieval
* Hybrid retrieval with and without reranking
* Selected chunk sizes
* Selected retrieval candidate counts

Each comparison should report:

* Quality change
* Latency change
* Cost change
* Dataset and configuration used
* Conclusion and chosen default

The project should report negative results honestly. A component should not remain enabled merely because it is fashionable.

---

## 23. Observability

Trace each query through:

```text
Query validation
→ Query rewriting
→ Full-text retrieval
→ Vector retrieval
→ Fusion
→ Reranking
→ Context assembly
→ Generation
→ Citation validation
```

Record:

* Request and trace IDs
* Stage-level latency
* Retrieved chunk IDs and scores
* Model names
* Input and output tokens
* Estimated cost
* Queue duration
* Errors and retries
* Fallback decisions
* Final status

Use structured logs and traces. Do not store secrets or complete document contents in normal logs.

---

## 24. User interface

Keep the interface focused and polished.

Required screens:

### Documents

* Upload a document
* View processing status
* View failure reason
* Retry processing
* Delete document

### Chat

* Ask questions
* Stream answers
* Stop generation
* Start a new conversation
* View conversation history
* Delete conversation
* Copy an answer
* View insufficient-evidence states

### Citations

* Open citation preview
* See source passage and surrounding context
* See document name, page, and section
* Open the original source where possible

### Debugger

* Inspect all retrieval and generation stages
* Inspect timings, scores, context, and citation mapping

### Evaluation

* Run a configured evaluation
* View progress
* Compare experiment results
* Inspect individual failures

The interface must include clear loading, empty, success, and error states.

---

## 25. Engineering quality

Required engineering practices:

* Clear module boundaries
* Typed API contracts
* Database migrations
* Configuration through environment variables
* `.env.example` without secrets
* Structured error responses
* Health and readiness endpoints
* Graceful dependency-failure handling
* Timeouts around external services
* Formatting and linting
* Frontend TypeScript checking
* Backend unit, integration, and workflow tests
* Continuous integration
* Reproducible local deployment
* Seed or sample document corpus
* Architecture and sequence diagrams
* Clear README

Critical integration tests:

* Re-uploading identical content does not duplicate active chunks
* A failed ingestion never becomes searchable
* Retrying ingestion produces one correct active version
* Deletion removes all searchable content
* Reprocessing never exposes a partially updated index
* Every citation maps to evidence supplied to the model
* Unknown citation markers are rejected or repaired safely
* Unanswerable questions trigger abstention
* Reranker timeout uses fused-order fallback
* Model-provider failure returns a clear error

---

## 26. Local deployment

The complete application should start with:

```bash
docker compose up
```

Recommended services:

* Next.js frontend
* FastAPI backend
* PostgreSQL with pgvector
* Local filesystem storage for uploaded documents

Recommended supporting tools:

* Optional OpenTelemetry export for tracing
* pytest for backend tests
* GitHub Actions for continuous integration

The exact frameworks may change, but parsing, chunking, embedding, retrieval, reranking, context assembly, generation, and evaluation must remain separate modules with clear interfaces.

---

# Delivery Plan

## Phase 1: Foundation and vertical slice

Build:

* Repository structure and local infrastructure
* Database schema and migrations
* PDF, Markdown, and TXT upload
* Synchronous ingestion pipeline
* Canonical document model
* Heading-aware chunking
* Embeddings and vector index
* Basic question answering
* Deterministic citations
* Minimal document and chat interfaces
* Initial tests and CI

Completion gate:

```text
A new user can start the system, upload a document, and receive a cited answer.
```

## Phase 2: Retrieval quality

Build:

* Full-text retrieval
* Reciprocal rank fusion
* Cross-encoder reranking
* Token-aware context assembly
* Abstention handling
* Conversational query rewriting
* Retrieval debugger

Completion gate:

```text
Every retrieval stage is inspectable, and hybrid retrieval is measured against baselines.
```

## Phase 3: Evaluation and experimentation

Build:

* Version-controlled evaluation dataset
* Retrieval metrics
* Answer and citation metrics
* Experiment runner
* Result reports or dashboard
* Regression thresholds in CI

Completion gate:

```text
Quality claims are reproducible from a clean checkout.
```

## Phase 4: Reliability and portfolio polish

Build:

* Complete failure handling and cleanup
* Observability and request tracing
* Performance and cost measurements
* Backend workflow tests
* Polished UI states
* Architecture documentation
* Benchmark report
* Demo dataset and demonstration video

Completion gate:

```text
The system is reliable, documented, measurable, and easy for another developer to run.
```

---

# Portfolio Completion Criteria

The project is complete when:

* The entire system starts with one documented command
* A fresh user can upload documents and receive cited answers
* Failed and incomplete documents never appear in retrieval
* Deleted documents never appear in subsequent retrieval
* Evaluation results are reproducible
* Hybrid retrieval is demonstrably compared with vector and full-text baselines
* Reranking has a measured benefit or is disabled with a documented reason
* Citation correctness is at least 95% on the curated dataset
* Invalid-citation rate is zero
* Abstention accuracy is at least 90% on the curated dataset
* Quality, latency, and cost tradeoffs are reported
* CI runs tests, linting, frontend TypeScript checks, and evaluation regression checks
* The repository contains architecture diagrams, benchmark results, known limitations, and setup instructions
* A short demonstration shows ingestion, chat, citations, abstention, retrieval debugging, and evaluation

Targets may be revised after establishing a baseline, but revisions must be recorded with supporting results.

---

# Out of Scope

* Authentication and role management
* Multi-tenancy
* Enterprise SSO
* User administration
* Department or document-level access control
* Enterprise PII-governance workflows
* Billing and cost-limit administration
* Kubernetes
* Agentic workflows
* Multi-agent systems
* GraphRAG
* Audio and video ingestion
* OCR-heavy scanned-document support
* Full multimodal image understanding
* External knowledge-source connectors
* Fine-tuning
* Advanced table reasoning
* Long-term personalized memory
* Native mobile applications

These features may be reconsidered only after the core RAG system meets its evaluation and reliability targets.
