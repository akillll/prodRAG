from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from sqlalchemy.orm import Session

from documents.models import DocumentRecord, DocumentVersionRecord
from documents.storage import LocalDocumentStorage, sanitize_filename

SUPPORTED_EXTENSIONS = {".pdf": "application/pdf", ".md": "text/markdown", ".txt": "text/plain"}


class UnsupportedDocumentType(ValueError):
    pass


@dataclass(frozen=True)
class UploadedDocument:
    filename: str | None
    mime_type: str | None
    content: bytes


class UploadDocumentService:
    def __init__(self, session: Session, storage: LocalDocumentStorage) -> None:
        self._session = session
        self._storage = storage

    def upload(self, uploaded: UploadedDocument) -> DocumentRecord:
        sanitized_filename = sanitize_filename(uploaded.filename)
        extension = Path(sanitized_filename).suffix.lower()
        if extension not in SUPPORTED_EXTENSIONS:
            supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
            raise UnsupportedDocumentType(f"supported file types are: {supported}")

        document_id = str(uuid4())
        storage_path = self._storage.store(
            document_id=document_id,
            filename=sanitized_filename,
            content=uploaded.content,
        )
        document = DocumentRecord(
            id=document_id,
            source_filename=uploaded.filename or sanitized_filename,
            sanitized_filename=sanitized_filename,
            file_extension=extension.removeprefix("."),
            mime_type=uploaded.mime_type or SUPPORTED_EXTENSIONS[extension],
            file_size_bytes=len(uploaded.content),
            storage_path=storage_path,
        )
        version = DocumentVersionRecord(
            id=str(uuid4()),
            document_id=document_id,
            version_number=1,
        )

        try:
            self._session.add_all([document, version])
            self._session.commit()
        except Exception:
            self._session.rollback()
            self._storage.delete(storage_path)
            raise

        self._session.refresh(document)
        return document
