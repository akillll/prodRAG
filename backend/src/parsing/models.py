from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import uuid4

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.session import Base


class ElementType(StrEnum):
    TITLE = "TITLE"
    HEADING = "HEADING"
    PARAGRAPH = "PARAGRAPH"
    LIST = "LIST"
    CODE_BLOCK = "CODE_BLOCK"


class CanonicalElementRecord(Base):
    __tablename__ = "canonical_elements"

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
    parent_element_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("canonical_elements.id", ondelete="SET NULL"),
    )
    element_type: Mapped[ElementType] = mapped_column(
        Enum(ElementType, name="element_type"),
        index=True,
    )
    content: Mapped[str] = mapped_column(Text)
    page_number: Mapped[int | None] = mapped_column(Integer)
    section_path: Mapped[list[str]] = mapped_column(JSON, default=list)
    element_order: Mapped[int] = mapped_column(Integer)
    start_offset: Mapped[int | None] = mapped_column(Integer)
    end_offset: Mapped[int | None] = mapped_column(Integer)
    token_count: Mapped[int | None] = mapped_column(Integer)
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    document_version: Mapped[DocumentVersionRecord] = relationship(
        "DocumentVersionRecord",
        back_populates="elements",
    )
    parent_element: Mapped[CanonicalElementRecord | None] = relationship(
        "CanonicalElementRecord",
        remote_side="CanonicalElementRecord.id",
    )
    chunks: Mapped[list[ChunkRecord]] = relationship(
        "ChunkRecord",
        back_populates="source_element",
    )


from chunking.models import ChunkRecord  # noqa: E402
from documents.models import DocumentVersionRecord  # noqa: E402
