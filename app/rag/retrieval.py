# app/rag/retrieval.py
"""
pgvector cosine-similarity search over document_embeddings, always
scoped through ChatbotScope (see rbac_scope.py) — this is the RBAC
enforcement point for the document/RAG path.
"""

import uuid

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.document_embedding import DocumentEmbedding
from app.models.task import Task
from app.rag.embedding_service import generate_embedding
from app.rag.rbac_scope import ChatbotScope


async def _resolve_source_label(
    session: AsyncSession, *, entity_type: str, entity_id: str
) -> str:
    """Turns (entity_type, entity_id) into a human-readable source name
    for citation, e.g. 'Task: Fix login bug' or 'Document: handbook.pdf'."""
    try:
        eid = uuid.UUID(entity_id)
    except ValueError:
        return "Unknown source"

    if entity_type == "task":
        result = await session.execute(select(Task.title).where(Task.id == eid))
        title = result.scalar_one_or_none()
        return f"Task: {title}" if title else "Task (deleted)"

    if entity_type == "comment":
        # Comments don't have their own title — cite the parent task instead.
        from app.models.comment import Comment

        result = await session.execute(
            select(Task.title)
            .join(Comment, Comment.task_id == Task.id)
            .where(Comment.id == eid)
        )
        title = result.scalar_one_or_none()
        return f"Comment on task: {title}" if title else "Comment (deleted)"

    if entity_type == "uploaded_document":
        result = await session.execute(
            select(Document.filename).where(Document.id == eid)
        )
        filename = result.scalar_one_or_none()
        return f"Document: {filename}" if filename else "Document (deleted)"

    return "Unknown source"


async def search_similar_chunks(
    session: AsyncSession,
    scope: ChatbotScope,
    *,
    query: str,
    top_k: int = 5,
) -> list[dict]:
    query_vector = generate_embedding(query)

    conditions = [DocumentEmbedding.organization_id == scope.organization_id]

    if not scope.is_admin_or_owner:
        if scope.allowed_project_ids:
            conditions.append(
                or_(
                    DocumentEmbedding.project_id.in_(scope.allowed_project_ids),
                    DocumentEmbedding.project_id.is_(None),
                )
            )
        else:
            conditions.append(DocumentEmbedding.project_id.is_(None))

    distance = DocumentEmbedding.embedding.cosine_distance(query_vector)

    stmt = (
        select(DocumentEmbedding, distance.label("distance"))
        .where(*conditions)
        .order_by(distance)
        .limit(top_k)
    )

    result = await session.execute(stmt)
    rows = result.all()

    results = []
    for chunk, dist in rows:
        source = await _resolve_source_label(
            session, entity_type=chunk.entity_type, entity_id=str(chunk.entity_id)
        )
        results.append(
            {
                "source": source,
                "content": chunk.content,
                "similarity_score": round(1 - dist, 4),
            }
        )
    return results
