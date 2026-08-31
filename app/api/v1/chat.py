# app/api/v1/chat.py
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.exceptions import InvalidCredentialsError
from app.db.session import get_db
from app.models.chat_message import ChatMessageRole
from app.models.user import User
from app.rag.chat_service import generate_title_from_message, get_chat_response
from app.rag.rbac_scope import resolve_scope
from app.repositories.chat_repository import ChatRepository
from app.schemas.chat import (
    ChatMessageRead,
    ChatRequest,
    ChatResponse,
    ChatSessionRead,
    ChatSessionWithMessages,
)
import json
from app.core.rate_limit import enforce_chat_rate_limit
from fastapi.responses import StreamingResponse

from app.rag.chat_service import generate_title_from_message, stream_chat_response

router = APIRouter(
    prefix="/organizations/{organization_id}/assistant",
    tags=["assistant"],
)


@router.post("/chat", response_model=ChatResponse)
async def chat(
    organization_id: uuid.UUID,
    payload: ChatRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ChatResponse:
    await enforce_chat_rate_limit(str(current_user.id))
    try:
        scope = await resolve_scope(
            db, organization_id=organization_id, user_id=current_user.id
        )
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e)) from e

    chat_repo = ChatRepository(db)

    if payload.session_id is not None:
        chat_session = await chat_repo.get_session(payload.session_id)
        if chat_session is None or chat_session.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found"
            )
    else:
        chat_session = await chat_repo.create_session(
            organization_id=organization_id,
            user_id=current_user.id,
            title=generate_title_from_message(payload.message),
        )
        await db.commit()

    history = await chat_repo.list_messages(chat_session.id)

    await chat_repo.add_message(
        session_id=chat_session.id, role=ChatMessageRole.USER, content=payload.message
    )

    reply = await get_chat_response(
        db, scope, user_message=payload.message, history=history
    )

    await chat_repo.add_message(
        session_id=chat_session.id, role=ChatMessageRole.ASSISTANT, content=reply
    )
    await chat_repo.touch_session(chat_session)
    await db.commit()

    return ChatResponse(reply=reply, session_id=chat_session.id)


@router.get("/sessions", response_model=list[ChatSessionRead])
async def list_chat_sessions(
    organization_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[ChatSessionRead]:
    sessions = await ChatRepository(db).list_sessions_for_user(
        organization_id=organization_id, user_id=current_user.id
    )
    return [ChatSessionRead.model_validate(s) for s in sessions]


@router.get("/sessions/{session_id}", response_model=ChatSessionWithMessages)
async def get_chat_session(
    organization_id: uuid.UUID,
    session_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ChatSessionWithMessages:
    chat_repo = ChatRepository(db)
    chat_session = await chat_repo.get_session(session_id)
    if chat_session is None or chat_session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found"
        )

    messages = await chat_repo.list_messages(session_id)
    return ChatSessionWithMessages(
        id=chat_session.id,
        title=chat_session.title,
        created_at=chat_session.created_at,
        updated_at=chat_session.updated_at,
        messages=[ChatMessageRead.model_validate(m) for m in messages],
    )


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_session(
    organization_id: uuid.UUID,
    session_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    chat_repo = ChatRepository(db)
    chat_session = await chat_repo.get_session(session_id)
    if chat_session is None or chat_session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found"
        )

    await chat_repo.delete_session(chat_session)
    await db.commit()


@router.post("/chat/stream")
async def chat_stream(
    organization_id: uuid.UUID,
    payload: ChatRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await enforce_chat_rate_limit(str(current_user.id))
    try:
        scope = await resolve_scope(
            db, organization_id=organization_id, user_id=current_user.id
        )
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e)) from e

    chat_repo = ChatRepository(db)

    if payload.session_id is not None:
        chat_session = await chat_repo.get_session(payload.session_id)
        if chat_session is None or chat_session.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found"
            )
    else:
        chat_session = await chat_repo.create_session(
            organization_id=organization_id,
            user_id=current_user.id,
            title=generate_title_from_message(payload.message),
        )
        await db.commit()

    history = await chat_repo.list_messages(chat_session.id)

    await chat_repo.add_message(
        session_id=chat_session.id, role=ChatMessageRole.USER, content=payload.message
    )
    await db.commit()

    session_id_str = str(chat_session.id)

    async def event_generator():
        full_text = ""
        yield f"event: session\ndata: {session_id_str}\n\n"

        async for piece in stream_chat_response(
            db, scope, user_message=payload.message, history=history
        ):
            full_text += piece
            yield f"data: {json.dumps({'delta': piece})}\n\n"

        await chat_repo.add_message(
            session_id=chat_session.id,
            role=ChatMessageRole.ASSISTANT,
            content=full_text or "Sorry, I couldn't generate a response.",
        )
        await chat_repo.touch_session(chat_session)
        await db.commit()

        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
