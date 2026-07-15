from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.session import Base


class ChunkRecord(Base):
    __tablename__ = "chunks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    document_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("documents.id", ondelete="CASCADE"),
        index=True,
    )
    document_version_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("document_versions.id", ondelete="CASCADE"),
        index=True,
    )
    source_element_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("canonical_elements.id", ondelete="SET NULL"),
        index=True,
    )
    previous_chunk_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("chunks.id", ondelete="SET NULL"),
    )
    next_chunk_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("chunks.id", ondelete="SET NULL"),
    )
    chunk_index: Mapped[int] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(Text)
    source_filename: Mapped[str] = mapped_column(String(255))
    page_number: Mapped[int | None] = mapped_column(Integer)
    section_path: Mapped[list[str]] = mapped_column(JSON, default=list)
    start_offset: Mapped[int | None] = mapped_column(Integer)
    end_offset: Mapped[int | None] = mapped_column(Integer)
    token_count: Mapped[int] = mapped_column(Integer)
    chunking_strategy: Mapped[str] = mapped_column(String(64))
    chunking_config_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    processing_version: Mapped[str] = mapped_column(String(64), default="ingestion-v1")
    parser_version: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    document_version: Mapped[DocumentVersionRecord] = relationship(
        "DocumentVersionRecord",
        back_populates="chunks",
    )
    source_element: Mapped[CanonicalElementRecord | None] = relationship(
        "CanonicalElementRecord",
        back_populates="chunks",
    )
    previous_chunk: Mapped[ChunkRecord | None] = relationship(
        "ChunkRecord",
        remote_side="ChunkRecord.id",
        foreign_keys=[previous_chunk_id],
    )
    next_chunk: Mapped[ChunkRecord | None] = relationship(
        "ChunkRecord",
        remote_side="ChunkRecord.id",
        foreign_keys=[next_chunk_id],
    )


from documents.models import DocumentVersionRecord  # noqa: E402
from parsing.models import CanonicalElementRecord  # noqa: E402
