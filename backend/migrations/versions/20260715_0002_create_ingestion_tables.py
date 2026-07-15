"""create ingestion tables

Revision ID: 20260715_0002
Revises: 20260708_0001
Create Date: 2026-07-15

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260715_0002"
down_revision: str | None = "20260708_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


document_status = postgresql.ENUM(
    "PROCESSING",
    "READY",
    "FAILED",
    "DELETING",
    name="document_status",
    create_type=False,
)

element_type = postgresql.ENUM(
    "TITLE",
    "HEADING",
    "PARAGRAPH",
    "LIST",
    "CODE_BLOCK",
    name="element_type",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    document_status.create(bind, checkfirst=True)
    element_type.create(bind, checkfirst=True)

    op.create_table(
        "documents",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("source_filename", sa.String(length=255), nullable=False),
        sa.Column("sanitized_filename", sa.String(length=255), nullable=False),
        sa.Column("file_extension", sa.String(length=16), nullable=False),
        sa.Column("mime_type", sa.String(length=255), nullable=False),
        sa.Column("file_size_bytes", sa.Integer(), nullable=False),
        sa.Column("content_hash", sa.String(length=128), nullable=True),
        sa.Column("storage_path", sa.String(length=1024), nullable=False),
        sa.Column("status", document_status, nullable=False),
        sa.Column("active_version_id", sa.String(length=36), nullable=True),
        sa.Column("latest_version_number", sa.Integer(), nullable=False),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_documents_content_hash"), "documents", ["content_hash"], unique=False)
    op.create_index(op.f("ix_documents_status"), "documents", ["status"], unique=False)

    op.create_table(
        "document_versions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("status", document_status, nullable=False),
        sa.Column("processing_version", sa.String(length=64), nullable=False),
        sa.Column("parser_version", sa.String(length=64), nullable=True),
        sa.Column("chunking_version", sa.String(length=64), nullable=True),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("activated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("document_id", "version_number", name="uq_document_version_number"),
    )
    op.create_index(
        op.f("ix_document_versions_document_id"),
        "document_versions",
        ["document_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_document_versions_status"),
        "document_versions",
        ["status"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_documents_active_version_id_document_versions",
        "documents",
        "document_versions",
        ["active_version_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_table(
        "canonical_elements",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("document_version_id", sa.String(length=36), nullable=False),
        sa.Column("parent_element_id", sa.String(length=36), nullable=True),
        sa.Column("element_type", element_type, nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=True),
        sa.Column("section_path", sa.JSON(), nullable=False),
        sa.Column("element_order", sa.Integer(), nullable=False),
        sa.Column("start_offset", sa.Integer(), nullable=True),
        sa.Column("end_offset", sa.Integer(), nullable=True),
        sa.Column("token_count", sa.Integer(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["document_version_id"],
            ["document_versions.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["parent_element_id"],
            ["canonical_elements.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_canonical_elements_document_id"),
        "canonical_elements",
        ["document_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_canonical_elements_document_version_id"),
        "canonical_elements",
        ["document_version_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_canonical_elements_element_type"),
        "canonical_elements",
        ["element_type"],
        unique=False,
    )

    op.create_table(
        "chunks",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("document_version_id", sa.String(length=36), nullable=False),
        sa.Column("source_element_id", sa.String(length=36), nullable=True),
        sa.Column("previous_chunk_id", sa.String(length=36), nullable=True),
        sa.Column("next_chunk_id", sa.String(length=36), nullable=True),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("source_filename", sa.String(length=255), nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=True),
        sa.Column("section_path", sa.JSON(), nullable=False),
        sa.Column("start_offset", sa.Integer(), nullable=True),
        sa.Column("end_offset", sa.Integer(), nullable=True),
        sa.Column("token_count", sa.Integer(), nullable=False),
        sa.Column("chunking_strategy", sa.String(length=64), nullable=False),
        sa.Column("chunking_config_json", sa.JSON(), nullable=False),
        sa.Column("processing_version", sa.String(length=64), nullable=False),
        sa.Column("parser_version", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["document_version_id"],
            ["document_versions.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["next_chunk_id"], ["chunks.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["previous_chunk_id"], ["chunks.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(
            ["source_element_id"],
            ["canonical_elements.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_chunks_document_id"), "chunks", ["document_id"], unique=False)
    op.create_index(
        op.f("ix_chunks_document_version_id"),
        "chunks",
        ["document_version_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_chunks_source_element_id"),
        "chunks",
        ["source_element_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_chunks_source_element_id"), table_name="chunks")
    op.drop_index(op.f("ix_chunks_document_version_id"), table_name="chunks")
    op.drop_index(op.f("ix_chunks_document_id"), table_name="chunks")
    op.drop_table("chunks")

    op.drop_index(op.f("ix_canonical_elements_element_type"), table_name="canonical_elements")
    op.drop_index(
        op.f("ix_canonical_elements_document_version_id"),
        table_name="canonical_elements",
    )
    op.drop_index(op.f("ix_canonical_elements_document_id"), table_name="canonical_elements")
    op.drop_table("canonical_elements")

    op.drop_constraint(
        "fk_documents_active_version_id_document_versions",
        "documents",
        type_="foreignkey",
    )

    op.drop_index(op.f("ix_document_versions_status"), table_name="document_versions")
    op.drop_index(op.f("ix_document_versions_document_id"), table_name="document_versions")
    op.drop_table("document_versions")

    op.drop_index(op.f("ix_documents_status"), table_name="documents")
    op.drop_index(op.f("ix_documents_content_hash"), table_name="documents")
    op.drop_table("documents")

    bind = op.get_bind()
    element_type.drop(bind, checkfirst=True)
    document_status.drop(bind, checkfirst=True)
