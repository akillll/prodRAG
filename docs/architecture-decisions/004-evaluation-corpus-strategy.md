# ADR-004: Evaluation Corpus Strategy

* Related tasks: `EVAL-001`, `EVAL-002`, `DEMO-001`

## Context

prodRAG is not only intended to answer questions over uploaded documents. It is also intended to support evaluation, debugging, and controlled comparisons between chunking, retrieval, and reranking choices.

That requires a corpus strategy that serves two different needs:

1. realistic document-format coverage
2. controlled, reproducible evaluation

Using only public external documents would improve realism but weaken evaluation control. Using only self-authored documents would improve control but reduce parser realism.

## Decision

The evaluation corpus uses three categories of source material:

1. owned documents
2. public documents
3. adversarial documents

Owned documents are the primary evaluation source. Public documents add realistic parsing behavior. Adversarial documents support prompt-injection and failure-case testing.

The current corpus structure is:

```text
evaluation/corpus/source/
├── owned/
├── public/
└── adversarial/
```

## Rationale

This split gives the project both control and realism.

Owned documents provide:

* exact-fact evaluation
* semantic question design
* conflicting-source cases
* unanswerable cases
* stable licensing

Public documents provide:

* real PDF structure
* real long-form text behavior
* parser and chunker stress without inventing artificial formatting

Adversarial documents provide:

* controlled prompt-injection content
* explicit tests that document content is treated as data, not instructions

## Consequences

### Benefits

* Evaluation remains defensible and reproducible.
* Public demo data can be redistributed safely.
* Parsing tests are not limited to artificial examples.
* Prompt-injection behavior can be tested intentionally.

### Costs

* The corpus needs curation rather than passive accumulation.
* Public-source licensing and provenance must still be tracked.
* The owned corpus must be maintained as the project evolves.

## Rejected alternatives

### Only external documents

Rejected because they make it harder to control answer keys, ambiguity, and benchmarking conditions.

### Only self-authored documents

Rejected because they do not provide enough real-world variation for PDF and long-text parsing behavior.

## Revisit conditions

This decision should be revisited if:

* the project grows into a larger benchmark suite
* multiple document domains need separate evaluation tracks
* external licensing requirements change the public corpus strategy

## Completion criteria

`ADR-004` is complete when:

* the repository contains owned, public, and adversarial corpus folders
* evaluation datasets are built primarily from controlled owned documents
* public files are selected intentionally for parser realism
