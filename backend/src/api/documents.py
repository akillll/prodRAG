from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.config import get_settings
from db.session import get_session
from documents.services import (
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


def get_upload_service(session: Annotated[Session, Depends(get_session)]) -> UploadDocumentService:
    storage = LocalDocumentStorage(get_settings().document_storage_path)
    return UploadDocumentService(session, storage)


@router.post("", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: Annotated[UploadFile, File(description="One PDF, Markdown, or text document")],
    service: Annotated[UploadDocumentService, Depends(get_upload_service)],
) -> DocumentUploadResponse:
    try:
        document = service.upload(
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

    return DocumentUploadResponse(
        id=document.id,
        filename=document.sanitized_filename,
        status=str(document.status),
        version_number=document.latest_version_number,
    )
