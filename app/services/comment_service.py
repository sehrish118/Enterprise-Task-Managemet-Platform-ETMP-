import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import CommentNotFoundError, NotCommentOwnerError
from app.models.comment import Comment
from app.repositories.comment_repository import CommentRepository


class CommentService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.comment_repo = CommentRepository(session)

    async def create_comment(
        self,
        *,
        organization_id: uuid.UUID,
        task_id: uuid.UUID,
        user_id: uuid.UUID,
        content: str,
        parent_comment_id: uuid.UUID | None,
    ) -> Comment:
        comment = await self.comment_repo.create(
            organization_id=organization_id,
            task_id=task_id,
            user_id=user_id,
            content=content,
            parent_comment_id=parent_comment_id,
        )
        await self.session.commit()
        return comment

    async def update_comment(
        self, *, comment_id: uuid.UUID, requesting_user_id: uuid.UUID, content: str
    ) -> Comment:
        comment = await self.comment_repo.get_by_id(comment_id)
        if comment is None:
            raise CommentNotFoundError(f"Comment {comment_id} not found")
        if comment.user_id != requesting_user_id:
            raise NotCommentOwnerError("You can only edit your own comments")

        comment = await self.comment_repo.update(comment, content=content)
        await self.session.commit()
        return comment

    async def delete_comment(
        self, *, comment_id: uuid.UUID, requesting_user_id: uuid.UUID
    ) -> None:
        comment = await self.comment_repo.get_by_id(comment_id)
        if comment is None:
            raise CommentNotFoundError(f"Comment {comment_id} not found")
        if comment.user_id != requesting_user_id:
            raise NotCommentOwnerError("You can only delete your own comments")

        await self.comment_repo.soft_delete(comment)
        await self.session.commit()

    async def list_comments(self, task_id: uuid.UUID) -> list[Comment]:
        return await self.comment_repo.list_by_task(task_id)

    async def list_comments_with_authors(self, task_id: uuid.UUID) -> list[tuple]:
        return await self.comment_repo.list_by_task_with_authors(task_id)
