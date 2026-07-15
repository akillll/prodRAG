from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.session import Base
from documents.status import DocumentStatus


class DocumentRecord(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    source_filename: Mapped[str] = mapped_column(String(255))
    sanitized_filename: Mapped[str] = mapped_column(String(255))
    file_extension: Mapped[str] = mapped_column(String(16))
    mime_type: Mapped[str] = mapped_column(String(255))
    file_size_bytes: Mapped[int] = mapped_column(Integer)
    content_hash: Mapped[str | None] = mapped_column(String(128), index=True)
    storage_path: Mapped[str] = mapped_column(String(1024))
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus, name="document_status"),
        default=DocumentStatus.PROCESSING,
        index=True,
    )
    active_version_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("document_versions.id", ondelete="SET NULL"),
        nullable=True,
    )
    latest_version_number: Mapped[int] = mapped_column(Integer, default=1)
    failure_reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    versions: Mapped[list[DocumentVersionRecord]] = relationship(
        "DocumentVersionRecord",
        back_populates="document",
        foreign_keys="DocumentVersionRecord.document_id",
        cascade="all, delete-orphan",
        order_by="DocumentVersionRecord.version_number",
    )
    active_version: Mapped[DocumentVersionRecord | None] = relationship(
        "DocumentVersionRecord",
        foreign_keys=[active_version_id],
        post_update=True,
    )


class DocumentVersionRecord(Base):
    __tablename__ = "document_versions"
    __table_args__ = (
        UniqueConstraint("document_id", "version_number", name="uq_document_version_number"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    document_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("documents.id", ondelete="CASCADE"),
        index=True,
    )
    version_number: Mapped[int] = mapped_column(Integer)
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus, name="document_status"),
        default=DocumentStatus.PROCESSING,
        index=True,
    )
    processing_version: Mapped[str] = mapped_column(String(64), default="ingestion-v1")
    parser_version: Mapped[str | None] = mapped_column(String(64))
    chunking_version: Mapped[str | None] = mapped_column(String(64))
    failure_reason: Mapped[str | None] = mapped_column(Text)
    activated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    document: Mapped[DocumentRecord] = relationship(
        "DocumentRecord",
        back_populates="versions",
        foreign_keys=[document_id],
    )
    elements: Mapped[list[CanonicalElementRecord]] = relationship(
        "CanonicalElementRecord",
        back_populates="document_version",
        cascade="all, delete-orphan",
    )
    chunks: Mapped[list[ChunkRecord]] = relationship(
        "ChunkRecord",
        back_populates="document_version",
        cascade="all, delete-orphan",
    )


from chunking.models import ChunkRecord  # noqa: E402
from parsing.models import CanonicalElementRecord  # noqa: E402
