# prodRAG

An evaluation-driven Retrieval-Augmented Generation system for learning and demonstrating how high-quality RAG pipelines are designed, measured, and debugged.

The project focuses on the core RAG lifecycle:

```text
Document upload
→ Parsing
→ Structure-aware chunking
→ Embedding
→ Hybrid retrieval
→ Reranking
→ Context assembly
→ Grounded generation
→ Citation validation
→ Evaluation
```

This is a local, single-user portfolio project. It intentionally excludes enterprise features such as authentication, role management, multi-tenancy, Kubernetes, and administrative governance workflows.

## Project status

The project is currently in the planning and architecture stage.

* [Feature specification](./Features.md)
* [Sprint backlog](./tasks.md)

The feature specification defines what will be built. The sprint backlog divides that scope into implementation tasks and delivery gates.

For local setup and daily commands, see [Local Development](./docs/local-development.md).

## Project goals

The system is intended to demonstrate:

* Traceable document ingestion and chunk lineage
* Structure-aware document processing
* Vector, lexical, and hybrid retrieval
* Reciprocal rank fusion and reranking
* Token-aware context assembly
* Evidence-grounded answers
* Deterministic, validated citations
* Honest insufficient-evidence responses
* Reproducible RAG evaluation
* Inspectable retrieval and generation pipelines
* Measured quality, latency, and cost tradeoffs

The main portfolio claim is:

> An evaluation-driven RAG system that makes retrieval decisions inspectable and measures how chunking, hybrid search, and reranking affect answer quality.

## Approved technology stack

### Frontend

| Technology | Purpose |
| --- | --- |
| Next.js | Web application framework |
| TypeScript | Type-safe frontend development |
| Tailwind CSS | Styling |
| shadcn/ui | Accessible UI primitives |
| Fetch API | HTTP requests to the backend |
| Server-Sent Events over Fetch | Streaming generated answers from POST requests |


### Backend

| Technology | Purpose |
| --- | --- |
| Python | Backend and RAG implementation language |
| FastAPI | HTTP API and streaming endpoints |
| Pydantic | Request, response, and configuration validation |
| SQLAlchemy 2 | Database access and persistence |
| Alembic | Database migrations |
| OpenAI Python SDK | Commercial OpenAI API integration |
| pytest | Unit and integration tests |
| Ruff | Python linting |

### Data and retrieval

| Technology | Purpose |
| --- | --- |
| PostgreSQL | Application data, document metadata, lineage, and conversations |
| pgvector | Vector storage and similarity retrieval |
| PostgreSQL full-text search | Lexical retrieval |
| Local filesystem | Original document storage for local development |

The first version deliberately avoids a separate search cluster and object-storage service. Storage implementations will be hidden behind interfaces so they can be replaced later without changing the RAG pipeline.

### Model APIs

The application uses the commercial OpenAI API.

OpenAI API usage includes:

* Text embeddings
* Query rewriting
* Grounded answer generation
* Structured responses
* Answer streaming
* Optional model-based evaluation

Model identifiers are configured through environment variables rather than hard-coded in application logic. This allows models to be changed and evaluated without modifying the pipeline.

The OpenAI SDK must remain inside provider adapters. Parsing, chunking, retrieval, citations, and evaluation must depend on internal interfaces rather than directly on provider-specific SDK types.

### Observability

| Technology | Purpose |
| --- | --- |
| OpenTelemetry | Vendor-neutral logs, traces, and metrics instrumentation |
| SigNoz | Unified logs, traces, metrics, exceptions, dashboards, and LLM observability |
| Structured JSON logging | Searchable and trace-correlated application events |

SigNoz Cloud is the initial target to avoid adding observability infrastructure to the local application stack. Telemetry must be optional, and the RAG system must continue operating when SigNoz is disabled or unavailable.

### Local development

| Technology | Purpose |
| --- | --- |
| Docker Compose | PostgreSQL and reproducible local services |
| npm | Frontend dependency management |
| Makefile or justfile | Common repository commands |
| GitHub Actions | Continuous integration |

## Repository structure

The project uses a monorepo with separate frontend and backend applications.

```text
prodRAG/
├── frontend/
│   ├── src/
│   │   ├── app/                    # Next.js routes and layouts
│   │   ├── components/             # Shared UI components
│   │   ├── features/
│   │   │   ├── documents/          # Upload and document status
│   │   │   ├── chat/               # Conversations and streaming answers
│   │   │   ├── citations/          # Citation and source previews
│   │   │   ├── debugger/           # Retrieval debugger
│   │   │   └── evaluation/         # Evaluation results
│   │   ├── hooks/
│   │   └── lib/                    # API client and utilities
│   └── package.json
│
├── backend/
│   ├── src/
│   │   ├── api/                    # FastAPI routes and dependencies
│   │   ├── core/                   # Configuration, errors, and logging
│   │   ├── db/                     # Sessions, models, and repositories
│   │   ├── documents/              # Upload, lifecycle, and deletion
│   │   ├── ingestion/              # Synchronous pipeline orchestration
│   │   ├── parsing/                # PDF, Markdown, and TXT parsers
│   │   ├── chunking/               # Chunking strategies
│   │   ├── embeddings/             # Embedding provider interface
│   │   ├── retrieval/              # Lexical, vector, and hybrid retrieval
│   │   ├── reranking/              # Reranking interface and implementation
│   │   ├── context/                # Context assembly
│   │   ├── generation/             # OpenAI generation adapter
│   │   ├── citations/              # Citation resolution and validation
│   │   ├── conversations/          # Conversation persistence and rewriting
│   │   ├── evaluation/             # Metrics, runners, and experiments
│   │   └── observability/          # OpenTelemetry instrumentation
│   ├── migrations/
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── fixtures/
│   ├── pyproject.toml              # Tooling and project configuration
│   ├── requirements.txt            # Pinned runtime dependencies
│   └── requirements-dev.txt        # Pinned development dependencies
│
├── evaluation/
│   ├── corpus/                     # Licensed sample documents
│   ├── datasets/                   # Version-controlled evaluation cases
│   ├── experiments/                # Experiment configurations
│   └── results/                    # Generated machine-readable results
│
├── docs/
│   ├── architecture/               # System and sequence diagrams
│   ├── adr/                        # Architecture decision records
│   └── benchmarks/                 # Methodology and benchmark reports
├── scripts/                        # Development and evaluation utilities
├── infra/                          # Local service configuration
├── docker-compose.yml
├── .env.example
├── Features.md
├── tasks.md
└── README.md
```

Folders will be added when their corresponding sprint begins. Empty architecture should not be created merely to match this diagram.

## System architecture

```text
┌──────────────────┐
│ Next.js frontend │
└────────┬─────────┘
         │ HTTP + SSE
         ▼
┌──────────────────┐
│ FastAPI backend  │
├──────────────────┤
│ Ingestion        │
│ Retrieval        │
│ Generation       │
│ Evaluation       │
└───────┬────┬─────┘
        │    │
        │    └──────────────► OpenAI API
        │
        ▼
┌──────────────────┐
│ PostgreSQL       │
│ + pgvector       │
│ + full-text      │
└──────────────────┘

FastAPI ── OpenTelemetry ──► SigNoz Cloud
```

## Ingestion architecture

Ingestion is synchronous in the first version:

```text
Upload request
→ Validate file
→ Store original
→ Parse structure
→ Create canonical elements
→ Chunk content
→ Request OpenAI embeddings
→ Store vectors and full-text data
→ Atomically mark document READY
→ Return response
```

The frontend keeps the request open and displays an uploading or processing state. This is an intentional tradeoff for a local, single-user project.

The pipeline itself remains independent from FastAPI:

```text
API route
→ Synchronous ingestion runner
→ Ingestion pipeline
```

This keeps the code testable without introducing a separate job system.

The first version does not use durable job infrastructure or automatic retry scheduling.

Failed documents are marked `FAILED` with a reason. The user may explicitly retry processing. All stages must be idempotent, and incomplete documents must never become searchable.

## Query architecture

```text
User question
→ Validate query
→ Rewrite conversational follow-up when required
→ Run vector retrieval
→ Run full-text retrieval
→ Fuse results with reciprocal rank fusion
→ Rerank candidates
→ Deduplicate and assemble token-bounded context
→ Assign deterministic source markers
→ Generate a grounded answer with OpenAI
→ Validate citation markers
→ Stream the answer and resolved citations
```

Only `READY` documents may participate in retrieval.

## Citation design

The model receives evidence blocks with deterministic source markers:

```text
[S1] Evidence from document A...
[S2] Evidence from document B...
```

The model may cite only those markers. It must never generate document IDs, chunk IDs, filenames, or page numbers directly.

After generation, the backend:

1. Extracts cited source markers.
2. Verifies that every marker exists in the supplied context.
3. Resolves markers to stored document and chunk metadata.
4. Rejects or safely repairs unknown citations.
5. Returns citations with source passages and surrounding context.

## Insufficient-evidence behavior

The application must abstain when:

* No relevant chunks are retrieved.
* Retrieved evidence does not support an answer.
* Sources conflict without a supported resolution.
* Required information is missing.
* Generated citations cannot be validated.

Expected response:

```text
The available documents do not contain enough evidence to answer this reliably.
```

Abstention thresholds will be tuned from evaluation results rather than chosen from arbitrary similarity scores.

## Observability plan

Each user question creates one distributed trace:

```text
rag.query
├── conversation.load
├── query.rewrite
├── retrieval.vector
├── retrieval.lexical
├── retrieval.fusion
├── retrieval.rerank
├── context.assemble
├── openai.generate
└── citations.validate
```

Trace and log attributes include:

* Request and trace IDs
* Conversation and message IDs
* Model identifiers
* Prompt and pipeline versions
* Document and chunk IDs
* Retrieval ranks and scores
* Candidate and selected-result counts
* Context token count
* Input and output tokens
* Estimated API cost
* Stage-level latency
* Errors and fallback decisions

Complete document content, secrets, and API keys must not be written to normal logs. Exact context may be captured only through an explicit development setting.

Initial metrics include:

```text
rag_queries_total
rag_query_duration_ms
retrieval_duration_ms
generation_duration_ms
ingestion_duration_ms
ingestion_failures_total
abstentions_total
invalid_citations_total
embedding_tokens_total
generation_input_tokens_total
generation_output_tokens_total
estimated_openai_cost
```

Evaluation datasets and authoritative experiment results remain in the repository or PostgreSQL. Selected scores are also emitted to SigNoz for dashboards and trace correlation.

## Evaluation strategy

The project will use a manually reviewed, version-controlled dataset containing:

* Exact-fact questions
* Semantic questions
* Multi-section questions
* Multi-document questions
* Follow-up questions
* Unanswerable questions
* Conflicting-source questions
* Prompt-injection cases

Retrieval evaluation includes:

* Recall@k
* Precision@k
* Hit rate
* Mean reciprocal rank
* NDCG@k
* Retrieval latency

Answer evaluation includes:

* Correctness
* Faithfulness
* Citation correctness
* Citation completeness
* Unsupported-claim rate
* Invalid-citation rate
* Abstention accuracy
* End-to-end latency
* Token usage and estimated cost

Experiments will compare:

* Fixed-token and heading-aware chunking
* Full-text and vector retrieval
* Vector and hybrid retrieval
* Hybrid retrieval with and without reranking
* Selected chunk sizes
* Selected candidate counts

Components remain enabled only when evaluation demonstrates sufficient value for their latency and cost.

## API contracts

FastAPI is the source of truth for the HTTP API schema.

## Configuration

Secrets and environment-specific values belong in environment variables. The committed `.env.example` will document all required settings without containing real credentials.

Planned configuration:

```dotenv
# Application
APP_ENV=development
APP_LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql+psycopg:///prodrag

# Document storage
DOCUMENT_STORAGE_PATH=./data/documents
MAX_UPLOAD_SIZE_MB=25

# OpenAI commercial API
OPENAI_API_KEY=
OPENAI_GENERATION_MODEL=
OPENAI_EMBEDDING_MODEL=
OPENAI_REQUEST_TIMEOUT_SECONDS=120

# Retrieval
VECTOR_CANDIDATE_COUNT=40
LEXICAL_CANDIDATE_COUNT=40
FINAL_CONTEXT_COUNT=8
MAX_CONTEXT_TOKENS=8000

# OpenTelemetry and SigNoz
OTEL_ENABLED=false
OTEL_SERVICE_NAME=prodrag-backend
OTEL_EXPORTER_OTLP_ENDPOINT=
OTEL_EXPORTER_OTLP_HEADERS=
OTEL_ENVIRONMENT=development
OTEL_CAPTURE_CONTENT=false
```

Real API keys must never be committed.

## Development commands

Backend dependencies use the standard Python workflow:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r backend/requirements-dev.txt
```

On Windows, activate the environment with `.venv\Scripts\activate`.

Backend commands:

```bash
cd backend
source venv/bin/activate
python -m pytest tests
ruff check src tests
uvicorn main:app --app-dir src --reload
```

Frontend commands:

```bash
cd frontend
npm run dev
npm run lint
npm run typecheck
```

Database commands:

```bash
docker-compose up -d postgres
cd backend
source venv/bin/activate
alembic -c migrations/alembic.ini upgrade head
```

## Backend testing strategy

Frontend unit, component, and browser automation tests are outside the project scope. The frontend remains intentionally small, while correctness is verified at the API and RAG-pipeline boundaries.

### Unit tests

Cover:

* Parsers
* Chunking strategies
* Reciprocal rank fusion
* Context assembly
* Citation-marker validation
* Evaluation metrics

### Integration tests

Verify:

* Identical uploads do not duplicate active chunks.
* Failed ingestion never becomes searchable.
* Retrying ingestion produces one correct active version.
* Deleting a document removes all searchable artifacts.
* Reprocessing never exposes partially updated indexes.
* Every citation maps to evidence supplied to the model.
* Unknown citation markers are rejected safely.
* Reranker failure uses the documented fallback.
* OpenAI API failures return clear application errors.

### Backend workflow tests

Cover the complete workflow:

```text
Upload document
→ Process document
→ Ask question
→ Receive streaming answer
→ Open citation
→ Inspect retrieval trace
```

The complete workflow is tested through backend APIs rather than browser automation. External API calls should be replaced with deterministic fakes in automated tests. A separate opt-in test suite may exercise the real OpenAI API.

## Architecture decisions

### Monorepo

Frontend, backend, evaluation assets, infrastructure, and documentation remain in one repository so API changes, experiments, and backend workflow tests can evolve together.

### Synchronous ingestion

The application is local and single-user, so a separate job system would add more complexity than value. The ingestion pipeline remains isolated from API routes so it stays testable.

### PostgreSQL for both retrieval modes

PostgreSQL, pgvector, and PostgreSQL full-text search provide vector, lexical, and metadata storage without introducing a separate search cluster.

### Commercial OpenAI API

The application uses hosted OpenAI models instead of operating local model infrastructure. Provider access remains behind internal interfaces to keep the pipeline testable and configuration-driven.

### Optional OpenTelemetry and SigNoz

Structured JSON logs are the default local debugging tool. OpenTelemetry export to SigNoz is optional and should not be required for the application to run.

### Explicit RAG pipeline

The core RAG pipeline will be implemented through explicit application modules rather than hidden behind a large orchestration framework. This makes retrieval behavior easier to understand, test, trace, and evaluate.

## Out of scope

The first release does not include:

* Authentication or role management
* Multi-tenancy
* Enterprise SSO
* User administration
* Department-level access control
* Enterprise PII-governance workflows
* Billing administration
* Separate job-processing infrastructure
* Kubernetes
* Agentic or multi-agent workflows
* GraphRAG
* Audio or video ingestion
* OCR-heavy scanned documents
* Full multimodal image understanding
* External knowledge connectors
* Fine-tuning
* Advanced table reasoning
* Long-term personalized memory
* Local model inference

## Completion criteria

The portfolio release is complete when:

* The system starts with one documented command.
* A user can upload a document and receive a cited answer.
* Failed and incomplete documents never appear in retrieval.
* Deleted documents never appear in later retrieval.
* Evaluation results are reproducible from a clean checkout.
* Hybrid retrieval is compared against lexical and vector baselines.
* Reranking is retained only when its measured benefit justifies it.
* Citation correctness reaches at least 95% on the curated dataset.
* Invalid-citation rate is zero.
* Abstention accuracy reaches at least 90% on the curated dataset.
* Quality, latency, and OpenAI API cost tradeoffs are documented.
* CI runs formatting, linting, frontend TypeScript checks, backend tests, and evaluation regression checks.
* Architecture diagrams, benchmark results, limitations, and setup instructions are complete.
* A short demo shows ingestion, chat, citations, abstention, retrieval debugging, evaluation, and SigNoz traces.

Targets may be revised after establishing a baseline, but revisions must be recorded with supporting evaluation results.
