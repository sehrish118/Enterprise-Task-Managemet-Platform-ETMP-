import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.exceptions import AttachmentNotFoundError
from app.db.session import get_db
from app.models.user import User
from app.schemas.attachment import AttachmentRead
from app.services.attachment_service import AttachmentService

router = APIRouter(
    prefix="/organizations/{organization_id}/tasks/{task_id}/attachments",
    tags=["attachments"],
)


@router.post("", response_model=AttachmentRead, status_code=status.HTTP_201_CREATED)
async def create_attachment(
    organization_id: uuid.UUID,
    task_id: uuid.UUID,
    original_filename: str,
    mime_type: str,
    size: int,
    file_url: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AttachmentRead:
    service = AttachmentService(db)
    attachment = await service.create_attachment(
        organization_id=organization_id,
        task_id=task_id,
        uploaded_by=current_user.id,
        original_filename=original_filename,
        mime_type=mime_type,
        size=size,
        file_url=file_url,
    )
    return AttachmentRead.model_validate(attachment)


@router.get("", response_model=list[AttachmentRead])
async def list_attachments(
    organization_id: uuid.UUID,
    task_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[AttachmentRead]:
    service = AttachmentService(db)
    attachments = await service.list_attachments(task_id)
    return [AttachmentRead.model_validate(a) for a in attachments]


@router.delete("/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attachment(
    organization_id: uuid.UUID,
    task_id: uuid.UUID,
    attachment_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    service = AttachmentService(db)
    # try:
    await service.delete_attachment(attachment_id)
    # except AttachmentNotFoundError as e:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
