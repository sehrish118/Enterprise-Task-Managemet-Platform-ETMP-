# app/repositories/document_repository.py
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document, DocumentStatus


class DocumentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        organization_id: uuid.UUID,
        project_id: uuid.UUID | None,
        uploaded_by: uuid.UUID,
        filename: str,
        storage_path: str,
        content_type: str,
    ) -> Document:
        document = Document(
            organization_id=organization_id,
            project_id=project_id,
            uploaded_by=uploaded_by,
            filename=filename,
            storage_path=storage_path,
            content_type=content_type,
            status=DocumentStatus.PROCESSING,
        )
        self.session.add(document)
        await self.session.flush()
        return document

    async def get_by_id(self, document_id: uuid.UUID) -> Document | None:
        result = await self.session.execute(
            select(Document).where(Document.id == document_id)
        )
        return result.scalar_one_or_none()

    async def update_status(
        self, document: Document, status: DocumentStatus
    ) -> Document:
        document.status = status
        await self.session.flush()
        return document

    async def list_by_organization(self, organization_id: uuid.UUID) -> list[Document]:
        result = await self.session.execute(
            select(Document)
            .where(Document.organization_id == organization_id)
            .order_by(Document.created_at.desc())
        )
        return list(result.scalars().all())
