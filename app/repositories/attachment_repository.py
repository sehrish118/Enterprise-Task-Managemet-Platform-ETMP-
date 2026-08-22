import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attachment import Attachment


class AttachmentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, attachment_id: uuid.UUID) -> Attachment | None:
        result = await self.session.execute(
            select(Attachment).where(
                Attachment.id == attachment_id, Attachment.deleted_at.is_(None)
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        organization_id: uuid.UUID,
        task_id: uuid.UUID,
        uploaded_by: uuid.UUID,
        original_filename: str,
        stored_filename: str,
        mime_type: str,
        size: int,
        file_url: str,
    ) -> Attachment:
        attachment = Attachment(
            organization_id=organization_id,
            task_id=task_id,
            uploaded_by=uploaded_by,
            original_filename=original_filename,
            stored_filename=stored_filename,
            mime_type=mime_type,
            size=size,
            file_url=file_url,
        )
        self.session.add(attachment)
        await self.session.flush()
        return attachment

    async def soft_delete(self, attachment: Attachment) -> None:
        attachment.deleted_at = datetime.now(timezone.utc)
        await self.session.flush()

    async def list_by_task(self, task_id: uuid.UUID) -> list[Attachment]:
        result = await self.session.execute(
            select(Attachment).where(
                Attachment.task_id == task_id, Attachment.deleted_at.is_(None)
            )
        )
        return list(result.scalars().all())
