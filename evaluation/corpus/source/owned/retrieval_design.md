# Retrieval Design Notes

## Retrieval modes

prodRAG is designed to compare three retrieval modes:

1. vector retrieval
2. full-text retrieval
3. hybrid retrieval

Hybrid retrieval combines vector and lexical results instead of replacing one with the other.

## Vector retrieval

Vector retrieval uses embeddings stored in `pgvector`. It is useful when the query and the source text use different wording but similar meaning.

Vector retrieval is weak when exact terms matter and the semantic model misses a keyword.

## Full-text retrieval

Full-text retrieval uses PostgreSQL text search. It is useful when the query shares exact words or phrases with the document.

Full-text retrieval is weak when the answer is phrased differently from the query.

## Hybrid retrieval

Hybrid retrieval is the default comparison target because it can recover from the weaknesses of either single retrieval mode.

Hybrid retrieval should remain enabled only if evaluation shows that it improves quality enough to justify added latency and complexity.

## Rank fusion

The project uses reciprocal rank fusion to combine lexical and vector candidates into one ranked list.

Reciprocal rank fusion is preferred because it is simple, robust, and easy to explain. It does not require score normalization between systems that produce incompatible scores.

## Reranking

Reranking is optional. It should be enabled only if experiments show a measurable benefit.

Reranking must have a timeout. If reranking fails or times out, the system must fall back to the fused ranking order instead of failing the whole request.

## Context assembly

Context assembly is responsible for:

1. removing duplicate chunks
2. merging useful adjacent chunks
3. enforcing token budgets
4. assigning deterministic source markers

The generation model must receive evidence blocks with source markers and must not invent new markers.

## Source diversity

Context assembly should preserve source diversity when it improves answer quality. A context window filled with near-duplicate chunks wastes tokens and reduces coverage.

## Abstention rule

The system must abstain when retrieved evidence is missing, contradictory, or insufficient for a supported answer.

Abstention thresholds should be tuned from evaluation data rather than chosen from arbitrary similarity-score intuition.
