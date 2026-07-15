# ADR-006: Commercial OpenAI API Over Local Models

* Related tasks: `EMB-001`, `EMB-002`, `GEN-001`, `GEN-002`

## Context

prodRAG requires model capabilities for:

1. embeddings
2. grounded answer generation
3. possible query rewriting
4. optional model-based evaluation later

Two broad approaches were possible:

1. use hosted commercial APIs
2. run local models and local inference infrastructure

Local models would give more deployment control, but they would also shift substantial effort into model hosting, GPU constraints, model selection, and inference operations.

## Decision

The project uses the commercial OpenAI API instead of local models.

OpenAI-specific code must stay inside provider adapters. The rest of the pipeline must depend on internal interfaces rather than provider SDK types.

## Rationale

This decision keeps the focus on the RAG system rather than inference infrastructure.

The project is meant to demonstrate:

* ingestion design
* chunking behavior
* retrieval quality
* citation grounding
* evaluation methodology

Running local models would consume time and complexity without improving those core goals enough for the current scope.

## Consequences

### Benefits

* Faster progress on retrieval and citation work.
* No local model hosting setup.
* Lower hardware requirements for development.
* Easier model swapping through configuration.

### Costs

* External API dependency.
* Usage cost and rate limits.
* Less control than self-hosted models.
* Benchmark results depend partly on provider model behavior.

## Rejected alternatives

### Local models for the first release

Rejected because model-serving infrastructure is outside the main learning goal of this project.

## Revisit conditions

This decision should be revisited if:

* offline operation becomes important
* API costs become a blocking issue
* local inference becomes part of a later deployment or research goal

## Completion criteria

`ADR-006` is complete when:

* embeddings and generation are planned around the OpenAI API
* provider-specific logic is isolated behind internal adapters
* the project does not require local model-serving infrastructure for the first release
