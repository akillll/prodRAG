from pathlib import Path

import pytest

from documents.models import DocumentRecord
from documents.services import (
    ListDocumentsService,
    UnsupportedDocumentType,
    UploadDocumentService,
    UploadedDocument,
)
from documents.status import DocumentStatus
from documents.storage import LocalDocumentStorage, sanitize_filename


class FakeSession:
    def __init__(
        self,
        *,
        commit_error: Exception | None = None,
        existing_document: object | None = None,
    ) -> None:
        self.records: list[object] = []
        self.commit_error = commit_error
        self.existing_document = existing_document
        self.rolled_back = False

    def add_all(self, records: list[object]) -> None:
        self.records.extend(records)

    def commit(self) -> None:
        if self.commit_error:
            raise self.commit_error

    def rollback(self) -> None:
        self.rolled_back = True

    def refresh(self, _record: object) -> None:
        pass

    def scalar(self, _statement: object) -> object | None:
        return self.existing_document


@pytest.mark.parametrize(
    ("filename", "expected"),
    [
        ("notes.md", "notes.md"),
        ("../../Quarterly Report.txt", "Quarterly-Report.txt"),
        (r"C:\uploads\proposal.pdf", "proposal.pdf"),
    ],
)
def test_sanitize_filename_removes_path_and_unsafe_characters(
    filename: str,
    expected: str,
) -> None:
    assert sanitize_filename(filename) == expected


def test_sanitize_filename_rejects_empty_names() -> None:
    with pytest.raises(ValueError, match="valid character"):
        sanitize_filename("../")


def test_upload_stores_original_and_creates_processing_records(tmp_path: Path) -> None:
    session = FakeSession()
    service = UploadDocumentService(session, LocalDocumentStorage(tmp_path))  # type: ignore[arg-type]

    result = service.upload(
        UploadedDocument(filename="notes.md", mime_type="text/markdown", content=b"# Notes")
    )
    document = result.document

    assert result.duplicate is False
    assert document.sanitized_filename == "notes.md"
    assert document.file_extension == "md"
    assert document.file_size_bytes == 7
    assert Path(document.storage_path).read_bytes() == b"# Notes"
    assert len(session.records) == 2


def test_upload_rejects_unsupported_extensions(tmp_path: Path) -> None:
    service = UploadDocumentService(FakeSession(), LocalDocumentStorage(tmp_path))  # type: ignore[arg-type]

    with pytest.raises(UnsupportedDocumentType):
        service.upload(UploadedDocument(filename="malware.exe", mime_type=None, content=b"x"))


def test_upload_returns_existing_active_document_for_duplicate_content(tmp_path: Path) -> None:
    storage_path = tmp_path / "existing-document" / "existing.txt"
    storage_path.parent.mkdir()
    storage_path.write_text("same")
    existing_document = DocumentRecord(
        id="existing-document",
        source_filename="existing.txt",
        sanitized_filename="existing.txt",
        file_extension="txt",
        mime_type="text/plain",
        file_size_bytes=4,
        storage_path=str(storage_path),
        status=DocumentStatus.PROCESSING,
    )
    session = FakeSession(existing_document=existing_document)
    service = UploadDocumentService(session, LocalDocumentStorage(tmp_path))  # type: ignore[arg-type]

    result = service.upload(UploadedDocument(filename="copy.txt", mime_type=None, content=b"same"))

    assert result.document is existing_document
    assert result.duplicate is True
    assert session.records == []
    assert list(tmp_path.rglob("*.txt")) == [storage_path]


def test_upload_ignores_duplicate_record_when_its_original_is_missing(tmp_path: Path) -> None:
    existing_document = DocumentRecord(
        id="missing-document",
        source_filename="missing.txt",
        sanitized_filename="missing.txt",
        file_extension="txt",
        mime_type="text/plain",
        file_size_bytes=4,
        storage_path=str(tmp_path / "missing-document" / "missing.txt"),
        status=DocumentStatus.PROCESSING,
    )
    session = FakeSession(existing_document=existing_document)
    service = UploadDocumentService(session, LocalDocumentStorage(tmp_path))  # type: ignore[arg-type]

    result = service.upload(UploadedDocument(filename="copy.txt", mime_type=None, content=b"same"))

    assert result.duplicate is False
    assert len(session.records) == 2


def test_document_list_excludes_records_with_missing_originals(tmp_path: Path) -> None:
    existing_path = tmp_path / "present-document" / "present.txt"
    existing_path.parent.mkdir()
    existing_path.write_text("present")
    present_document = DocumentRecord(
        id="present-document",
        source_filename="present.txt",
        sanitized_filename="present.txt",
        file_extension="txt",
        mime_type="text/plain",
        file_size_bytes=7,
        storage_path=str(existing_path),
    )
    missing_document = DocumentRecord(
        id="missing-document",
        source_filename="missing.txt",
        sanitized_filename="missing.txt",
        file_extension="txt",
        mime_type="text/plain",
        file_size_bytes=7,
        storage_path=str(tmp_path / "missing-document" / "missing.txt"),
    )

    class ListSession:
        def scalars(self, _statement: object) -> list[DocumentRecord]:
            return [present_document, missing_document]

    service = ListDocumentsService(ListSession(), LocalDocumentStorage(tmp_path))  # type: ignore[arg-type]

    assert service.list_documents() == [present_document]


def test_upload_removes_original_when_database_commit_fails(tmp_path: Path) -> None:
    session = FakeSession(commit_error=RuntimeError("database unavailable"))
    service = UploadDocumentService(session, LocalDocumentStorage(tmp_path))  # type: ignore[arg-type]

    with pytest.raises(RuntimeError, match="database unavailable"):
        service.upload(UploadedDocument(filename="notes.txt", mime_type=None, content=b"notes"))

    assert session.rolled_back is True
    assert list(tmp_path.rglob("*")) == []
