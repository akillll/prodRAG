from chunking.models import ChunkRecord
from documents import DocumentStatus
from documents.models import DocumentRecord, DocumentVersionRecord
from parsing.models import CanonicalElementRecord, ElementType


def test_document_related_tables_are_registered() -> None:
    assert DocumentRecord.__tablename__ == "documents"
    assert DocumentVersionRecord.__tablename__ == "document_versions"
    assert CanonicalElementRecord.__tablename__ == "canonical_elements"
    assert ChunkRecord.__tablename__ == "chunks"


def test_document_schema_defaults_match_ingestion_contract() -> None:
    document = DocumentRecord(
        source_filename="sample.md",
        sanitized_filename="sample.md",
        file_extension="md",
        mime_type="text/markdown",
        file_size_bytes=128,
        storage_path="data/documents/sample.md",
    )
    version = DocumentVersionRecord(version_number=1)
    element = CanonicalElementRecord(
        document_id="doc-1",
        document_version_id="ver-1",
        element_type=ElementType.PARAGRAPH,
        content="hello world",
        section_path=["Introduction"],
        element_order=1,
    )
    chunk = ChunkRecord(
        document_id="doc-1",
        document_version_id="ver-1",
        chunk_index=0,
        content="hello world",
        source_filename="sample.md",
        section_path=["Introduction"],
        token_count=2,
        chunking_strategy="heading-aware",
    )

    assert document.__table__.c.status.default.arg is DocumentStatus.PROCESSING
    assert document.__table__.c.latest_version_number.default.arg == 1
    assert version.__table__.c.status.default.arg is DocumentStatus.PROCESSING
    assert version.__table__.c.processing_version.default.arg == "ingestion-v1"
    assert callable(element.__table__.c.metadata_json.default.arg)
    assert element.__table__.c.metadata_json.default.arg.__name__ == "dict"
    assert callable(chunk.__table__.c.chunking_config_json.default.arg)
    assert chunk.__table__.c.chunking_config_json.default.arg.__name__ == "dict"
    assert chunk.__table__.c.processing_version.default.arg == "ingestion-v1"
