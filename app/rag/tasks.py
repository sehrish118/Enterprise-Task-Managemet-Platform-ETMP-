# app/rag/tasks.py
import asyncio
import uuid

from sqlalchemy import select

from app.core.celery_app import celery_app
from app.core.logging import get_logger
from app.db.session import async_session_local
from app.models.document_embedding import DocumentEmbedding
from app.rag.embedding_service import generate_embedding
from app.models.document import Document, DocumentStatus
from app.rag.chunking import chunk_text
from app.rag.text_extraction import extract_text

logger = get_logger(__name__)


async def _upsert_embedding(
    organization_id: str,
    project_id: str | None,
    entity_type: str,
    entity_id: str,
    content: str,
) -> None:
    """
    Generates the embedding and writes/updates the row.
    Upsert-by-(entity_type, entity_id): if a task/comment/document is
    edited, we regenerate its embedding rather than accumulating stale
    duplicate rows.
    """
    vector = generate_embedding(content)

    async with async_session_local() as session:
        result = await session.execute(
            select(DocumentEmbedding).where(
                DocumentEmbedding.entity_type == entity_type,
                DocumentEmbedding.entity_id == uuid.UUID(entity_id),
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.content = content
            existing.embedding = vector
        else:
            session.add(
                DocumentEmbedding(
                    organization_id=uuid.UUID(organization_id),
                    project_id=uuid.UUID(project_id) if project_id else None,
                    entity_type=entity_type,
                    entity_id=uuid.UUID(entity_id),
                    content=content,
                    embedding=vector,
                )
            )
        await session.commit()


@celery_app.task(
    name="rag.embed_entity",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
)
def embed_entity_task(
    self,
    organization_id: str,
    entity_type: str,
    entity_id: str,
    content: str,
    project_id: str | None = None,
) -> None:
    """
    Entry point called from services (e.g. after a Task or Comment is
    created/updated, or a document is uploaded).

    All ids are passed as strings because Celery serializes task args as
    JSON — UUID objects don't survive that, so callers must str(uuid) them.
    """
    try:
        logger.info(f"Embedding {entity_type}={entity_id} (org={organization_id})")
        asyncio.run(
            _upsert_embedding(
                organization_id=organization_id,
                project_id=project_id,
                entity_type=entity_type,
                entity_id=entity_id,
                content=content,
            )
        )
    except Exception as exc:
        logger.error(
            f"Embedding failed for {entity_type}={entity_id}: {exc}", exc_info=True
        )
        raise self.retry(exc=exc)


async def _delete_embedding(entity_type: str, entity_id: str) -> None:
    async with async_session_local() as session:
        result = await session.execute(
            select(DocumentEmbedding).where(
                DocumentEmbedding.entity_type == entity_type,
                DocumentEmbedding.entity_id == uuid.UUID(entity_id),
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            await session.delete(existing)
            await session.commit()


@celery_app.task(
    name="rag.delete_embedding",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
)
def delete_embedding_task(self, entity_type: str, entity_id: str) -> None:
    try:
        logger.info(f"Deleting embedding for {entity_type}={entity_id}")
        asyncio.run(_delete_embedding(entity_type=entity_type, entity_id=entity_id))
    except Exception as exc:
        logger.error(
            f"Delete embedding failed for {entity_type}={entity_id}: {exc}",
            exc_info=True,
        )
        raise self.retry(exc=exc)


async def _process_document(document_id: str) -> None:
    from app.rag.relevance_check import is_company_related

    async with async_session_local() as session:
        result = await session.execute(
            select(Document).where(Document.id == uuid.UUID(document_id))
        )
        document = result.scalar_one_or_none()
        if document is None:
            logger.error(f"Document {document_id} not found for processing")
            return

        try:
            raw_text = extract_text(document.storage_path, document.content_type)

            # Relevance gate — runs BEFORE any chunking/embedding.
            is_related, reason = await is_company_related(raw_text)
            if not is_related:
                document.status = DocumentStatus.REJECTED
                document.rejection_reason = reason
                await session.commit()
                logger.info(f"Document {document_id} rejected: {reason}")
                return

            chunks = chunk_text(raw_text)

            if not chunks:
                document.status = DocumentStatus.FAILED
                await session.commit()
                return

            for index, chunk in enumerate(chunks):
                vector = generate_embedding(chunk)
                session.add(
                    DocumentEmbedding(
                        organization_id=document.organization_id,
                        project_id=document.project_id,
                        entity_type="uploaded_document",
                        entity_id=document.id,
                        chunk_index=index,
                        content=chunk,
                        embedding=vector,
                    )
                )

            document.status = DocumentStatus.COMPLETED
            await session.commit()

        except Exception:
            document.status = DocumentStatus.FAILED
            await session.commit()
            raise


@celery_app.task(
    name="rag.process_document",
    bind=True,
    max_retries=2,
    default_retry_delay=30,
)
def process_document_task(self, document_id: str) -> None:
    try:
        logger.info(f"Processing document {document_id}")
        asyncio.run(_process_document(document_id))
    except Exception as exc:
        logger.error(
            f"Document processing failed for {document_id}: {exc}", exc_info=True
        )
        raise self.retry(exc=exc)
