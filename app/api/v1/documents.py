# app/api/v1/documents.py
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_current_user, require_permission
from app.enums.permissions import Permissions

from app.core.exceptions import UnsupportedFileTypeError
from app.db.session import get_db
from app.models.user import User
from app.schemas.document import DocumentRead
from app.services.document_service import DocumentService

router = APIRouter(
    prefix="/organizations/{organization_id}/documents",
    tags=["documents"],
)


@router.post("", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def upload_document(
    organization_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    file: Annotated[UploadFile, File(...)],
    _: Annotated[None, Depends(require_permission(Permissions.DOCUMENT_UPLOAD))],
    project_id: uuid.UUID | None = None,
) -> DocumentRead:
    service = DocumentService(db)
    try:
        document = await service.upload_document(
            organization_id=organization_id,
            project_id=project_id,
            uploaded_by=current_user.id,
            file=file,
        )
    except UnsupportedFileTypeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
    return DocumentRead.model_validate(document)


@router.get("", response_model=list[DocumentRead])
async def list_documents(
    organization_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[DocumentRead]:
    service = DocumentService(db)
    documents = await service.list_documents(organization_id)
    return [DocumentRead.model_validate(d) for d in documents]


@router.get("/{document_id}", response_model=DocumentRead)
async def get_document(
    organization_id: uuid.UUID,
    document_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DocumentRead:
    document = await DocumentService(db).document_repo.get_by_id(document_id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )
    return DocumentRead.model_validate(document)
