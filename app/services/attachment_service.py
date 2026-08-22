import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AttachmentNotFoundError
from app.models.attachment import Attachment
from app.repositories.attachment_repository import AttachmentRepository


class AttachmentService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.attachment_repo = AttachmentRepository(session)

    async def create_attachment(
        self,
        *,
        organization_id: uuid.UUID,
        task_id: uuid.UUID,
        uploaded_by: uuid.UUID,
        original_filename: str,
        mime_type: str,
        size: int,
        file_url: str,
    ) -> Attachment:
        stored_filename = f"{uuid.uuid4()}_{original_filename}"
        attachment = await self.attachment_repo.create(
            organization_id=organization_id,
            task_id=task_id,
            uploaded_by=uploaded_by,
            original_filename=original_filename,
            stored_filename=stored_filename,
            mime_type=mime_type,
            size=size,
            file_url=file_url,
        )
        await self.session.commit()
        return attachment

    async def delete_attachment(self, attachment_id: uuid.UUID) -> None:
        attachment = await self.attachment_repo.get_by_id(attachment_id)
        if attachment is None:
            raise AttachmentNotFoundError(f"Attachment {attachment_id} not found")
        await self.attachment_repo.soft_delete(attachment)
        await self.session.commit()

    async def list_attachments(self, task_id: uuid.UUID) -> list[Attachment]:
        return await self.attachment_repo.list_by_task(task_id)
