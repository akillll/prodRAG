from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.config import get_settings
from db.session import get_session
from documents.services import (
    ListDocumentsService,
    UnsupportedDocumentType,
    UploadDocumentService,
    UploadedDocument,
)
from documents.storage import LocalDocumentStorage

router = APIRouter(prefix="/documents", tags=["documents"])


class DocumentUploadResponse(BaseModel):
    id: str
    filename: str
    status: str
    version_number: int
    duplicate: bool


class DocumentStatusResponse(BaseModel):
    id: str
    filename: str
    status: str
    failure_reason: str | None
    file_size_bytes: int
    created_at: str


def get_upload_service(session: Annotated[Session, Depends(get_session)]) -> UploadDocumentService:
    storage = LocalDocumentStorage(get_settings().document_storage_path)
    return UploadDocumentService(session, storage)


def get_list_documents_service(
    session: Annotated[Session, Depends(get_session)],
) -> ListDocumentsService:
    return ListDocumentsService(session, LocalDocumentStorage(get_settings().document_storage_path))


@router.post("", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: Annotated[UploadFile, File(description="One PDF, Markdown, or text document")],
    service: Annotated[UploadDocumentService, Depends(get_upload_service)],
    response: Response,
) -> DocumentUploadResponse:
    try:
        result = service.upload(
            UploadedDocument(
                filename=file.filename,
                mime_type=file.content_type,
                content=await file.read(),
            )
        )
    except (UnsupportedDocumentType, ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=str(error),
        ) from error
    finally:
        await file.close()

    if result.duplicate:
        response.status_code = status.HTTP_200_OK

    document = result.document
    return DocumentUploadResponse(
        id=document.id,
        filename=document.sanitized_filename,
        status=str(document.status),
        version_number=document.latest_version_number,
        duplicate=result.duplicate,
    )


@router.get("", response_model=list[DocumentStatusResponse])
def list_documents(
    service: Annotated[ListDocumentsService, Depends(get_list_documents_service)],
) -> list[DocumentStatusResponse]:
    return [
        DocumentStatusResponse(
            id=document.id,
            filename=document.sanitized_filename,
            status=str(document.status),
            failure_reason=document.failure_reason,
            file_size_bytes=document.file_size_bytes,
            created_at=document.created_at.isoformat(),
        )
        for document in service.list_documents()
    ]
