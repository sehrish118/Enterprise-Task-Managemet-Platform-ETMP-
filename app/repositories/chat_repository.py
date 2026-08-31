# app/repositories/chat_repository.py
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat_message import ChatMessage, ChatMessageRole
from app.models.chat_session import ChatSession


class ChatRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_session(
        self, *, organization_id: uuid.UUID, user_id: uuid.UUID, title: str = "New Chat"
    ) -> ChatSession:
        chat_session = ChatSession(
            organization_id=organization_id, user_id=user_id, title=title
        )
        self.session.add(chat_session)
        await self.session.flush()
        return chat_session

    async def get_session(self, session_id: uuid.UUID) -> ChatSession | None:
        result = await self.session.execute(
            select(ChatSession).where(ChatSession.id == session_id)
        )
        return result.scalar_one_or_none()

    async def list_sessions_for_user(
        self, *, organization_id: uuid.UUID, user_id: uuid.UUID
    ) -> list[ChatSession]:
        result = await self.session.execute(
            select(ChatSession)
            .where(
                ChatSession.organization_id == organization_id,
                ChatSession.user_id == user_id,
            )
            .order_by(ChatSession.updated_at.desc())
        )
        return list(result.scalars().all())

    async def update_title(self, chat_session: ChatSession, title: str) -> ChatSession:
        chat_session.title = title
        await self.session.flush()
        return chat_session

    async def touch_session(self, chat_session: ChatSession) -> None:
        """Bumps updated_at so recently-active chats float to the top of
        the sidebar list, like ChatGPT/Claude do."""
        chat_session.updated_at = datetime.now(timezone.utc)
        await self.session.flush()

    async def delete_session(self, chat_session: ChatSession) -> None:
        await self.session.delete(chat_session)

    async def add_message(
        self, *, session_id: uuid.UUID, role: ChatMessageRole, content: str
    ) -> ChatMessage:
        message = ChatMessage(session_id=session_id, role=role, content=content)
        self.session.add(message)
        await self.session.flush()
        return message

    async def list_messages(self, session_id: uuid.UUID) -> list[ChatMessage]:
        result = await self.session.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at)
        )
        return list(result.scalars().all())
