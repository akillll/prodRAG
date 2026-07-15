# API Contract Notes

## `POST /documents`

Uploads a single document for synchronous ingestion.

Expected behavior:

1. validate file type
2. validate file size
3. reject empty files
4. store the original file
5. run synchronous processing
6. return document metadata and processing status

Example response shape:

```json
{
  "document_id": "doc_001",
  "filename": "retrieval_design.md",
  "status": "READY"
}
```

## `GET /documents`

Returns uploaded documents and their statuses.

Expected behavior:

1. list current documents
2. expose status and failure information
3. support frontend status display

## `POST /chat`

Creates a retrieval and generation request against ready documents.

Expected behavior:

1. validate query
2. retrieve evidence from ready documents only
3. assemble token-bounded context
4. stream grounded answer events
5. return citations that map to supplied source markers

## `GET /health`

Confirms the API is reachable.

Expected response:

```json
{
  "status": "ok",
  "app": "prodRAG",
  "environment": "local"
}
```

## `GET /ready`

Confirms the application can reach the database.

Expected response:

```json
{
  "status": "ready"
}
```

## Error response expectations

Errors should be explicit enough for debugging and UI display.

Useful cases include:

1. unsupported file type
2. corrupt file
3. empty file
4. database unavailable
5. provider failure

## Streaming expectation

The chat response is expected to use server-sent events so the frontend can display partial answer progress without waiting for a complete response.
