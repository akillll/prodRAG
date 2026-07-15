# prodRAG Handbook

## Purpose

prodRAG is an evaluation-driven Retrieval-Augmented Generation system built to study how document ingestion, chunking, retrieval, and citations behave in a local, single-user application.

The project is not intended to be an enterprise platform. It does not include authentication, role management, multi-tenancy, billing, or Kubernetes in the first release.

## Supported document formats

The first release accepts exactly three document formats:

1. PDF
2. Markdown
3. TXT

Only one file may be uploaded per request.

## Ingestion lifecycle

The ingestion pipeline runs synchronously in the first release. The expected processing sequence is:

1. Validate file
2. Store original
3. Parse structure
4. Normalize content
5. Chunk text
6. Embed chunks
7. Index chunks
8. Activate document

Incomplete documents must never become searchable.

## Document statuses

Documents use four primary statuses:

1. `PROCESSING`
2. `READY`
3. `FAILED`
4. `DELETING`

Only documents in `READY` status are searchable.

## Duplicate handling

The system calculates a content hash for each uploaded file. Uploading identical content should not create duplicate active documents. Identical uploads should be handled idempotently.

## Citation rules

Answers must be grounded in retrieved evidence. The model may cite only source markers supplied in the assembled context. Source markers are deterministic and follow the pattern `[S1]`, `[S2]`, and so on.

The backend resolves source markers to document metadata such as document ID, chunk ID, page number, section path, and passage text.

## Insufficient evidence behavior

If the retrieved context does not contain enough evidence to answer a question reliably, the system must abstain instead of inventing an answer.

The preferred abstention message is:

`The available documents do not contain enough evidence to answer this reliably.`

## Known limitations

The first release does not support:

1. OCR-heavy scanned PDFs
2. audio or video ingestion
3. multi-file upload in a single request
4. external knowledge connectors
5. enterprise access control

## Operating model

The local filesystem is used for uploaded document storage in development. PostgreSQL stores application data, document metadata, chunk lineage, and retrieval indexes.
