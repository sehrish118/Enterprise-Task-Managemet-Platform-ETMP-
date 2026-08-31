# app/services/document_service.py
import uuid
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import UnsupportedFileTypeError
from app.models.document import Document
from app.rag.tasks import process_document_task
from app.repositories.document_repository import DocumentRepository

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
}

MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB


class DocumentService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.document_repo = DocumentRepository(session)

    async def upload_document(
        self,
        *,
        organization_id: uuid.UUID,
        project_id: uuid.UUID | None,
        uploaded_by: uuid.UUID,
        file: UploadFile,
    ) -> Document:
        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise UnsupportedFileTypeError(
                f"Unsupported file type: {file.content_type}. Allowed: PDF, DOCX, TXT."
            )

        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE_BYTES:
            raise UnsupportedFileTypeError("File exceeds the 20MB size limit.")

        # Files are namespaced by organization to keep tenants isolated
        # on disk, mirroring the DB-level tenant isolation.
        org_dir = Path(settings.UPLOAD_DIR) / str(organization_id)
        org_dir.mkdir(parents=True, exist_ok=True)

        safe_name = f"{uuid.uuid4()}_{file.filename}"
        storage_path = org_dir / safe_name
        storage_path.write_bytes(contents)

        document = await self.document_repo.create(
            organization_id=organization_id,
            project_id=project_id,
            uploaded_by=uploaded_by,
            filename=file.filename or safe_name,
            storage_path=str(storage_path),
            content_type=file.content_type,
        )
        await self.session.commit()

        process_document_task.delay(document_id=str(document.id))

        return document

    async def list_documents(self, organization_id: uuid.UUID) -> list[Document]:
        return await self.document_repo.list_by_organization(organization_id)
