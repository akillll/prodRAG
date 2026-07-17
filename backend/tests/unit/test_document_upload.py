from pathlib import Path

import pytest

from documents.services import UnsupportedDocumentType, UploadDocumentService, UploadedDocument
from documents.storage import LocalDocumentStorage, sanitize_filename


class FakeSession:
    def __init__(self, *, commit_error: Exception | None = None) -> None:
        self.records: list[object] = []
        self.commit_error = commit_error
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

    document = service.upload(
        UploadedDocument(filename="notes.md", mime_type="text/markdown", content=b"# Notes")
    )

    assert document.sanitized_filename == "notes.md"
    assert document.file_extension == "md"
    assert document.file_size_bytes == 7
    assert Path(document.storage_path).read_bytes() == b"# Notes"
    assert len(session.records) == 2


def test_upload_rejects_unsupported_extensions(tmp_path: Path) -> None:
    service = UploadDocumentService(FakeSession(), LocalDocumentStorage(tmp_path))  # type: ignore[arg-type]

    with pytest.raises(UnsupportedDocumentType):
        service.upload(UploadedDocument(filename="malware.exe", mime_type=None, content=b"x"))


def test_upload_removes_original_when_database_commit_fails(tmp_path: Path) -> None:
    session = FakeSession(commit_error=RuntimeError("database unavailable"))
    service = UploadDocumentService(session, LocalDocumentStorage(tmp_path))  # type: ignore[arg-type]

    with pytest.raises(RuntimeError, match="database unavailable"):
        service.upload(UploadedDocument(filename="notes.txt", mime_type=None, content=b"notes"))

    assert session.rolled_back is True
    assert list(tmp_path.rglob("*")) == []
