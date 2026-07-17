from fastapi.testclient import TestClient

from api.documents import get_upload_service
from documents.models import DocumentRecord
from documents.services import UploadedDocument
from documents.status import DocumentStatus
from main import app


class FakeUploadService:
    def __init__(self) -> None:
        self.uploaded: UploadedDocument | None = None

    def upload(self, uploaded: UploadedDocument) -> DocumentRecord:
        self.uploaded = uploaded
        return DocumentRecord(
            id="document-1",
            source_filename="notes.md",
            sanitized_filename="notes.md",
            file_extension="md",
            mime_type="text/markdown",
            file_size_bytes=len(uploaded.content),
            storage_path="/tmp/documents/document-1/notes.md",
            status=DocumentStatus.PROCESSING,
            latest_version_number=1,
        )


def test_post_documents_accepts_one_multipart_file() -> None:
    service = FakeUploadService()
    app.dependency_overrides[get_upload_service] = lambda: service
    try:
        response = TestClient(app).post(
            "/documents",
            files={"file": ("notes.md", b"# Notes", "text/markdown")},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json() == {
        "id": "document-1",
        "filename": "notes.md",
        "status": "PROCESSING",
        "version_number": 1,
    }
    assert service.uploaded == UploadedDocument(
        filename="notes.md",
        mime_type="text/markdown",
        content=b"# Notes",
    )
