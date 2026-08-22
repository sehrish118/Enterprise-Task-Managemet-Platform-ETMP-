"""Web routes for tasks — reuses TaskService, TaskStatusService, CommentService."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    TaskStatusNotFoundError,
    UserAlreadyAssignedError,
    UserNotFoundError,
    CommentNotFoundError,
    NotCommentOwnerError,
    InvalidCredentialsError,
    TaskStatusAlreadyExistsError,
)
from app.db.session import get_db
from app.models.user import User
from app.services.comment_service import CommentService
from app.services.task_service import TaskService
from app.services.task_status_service import TaskStatusService
from app.web.dependencies import get_current_user_from_cookie, require_permission_web
from app.services.attachment_service import AttachmentService
from app.enums.permissions import Permissions


router = APIRouter(tags=["web-tasks"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/organizations/{organization_id}/projects/{project_id}/tasks")
async def list_tasks(
    request: Request,
    organization_id: str,
    project_id: str,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
    search: str | None = None,
    priority: str | None = None,
):
    task_service = TaskService(db)
    status_service = TaskStatusService(db)
    tasks, _ = await task_service.list_tasks(
        uuid.UUID(project_id),
        search=search,
        priority=priority or None,
        page=1,
        page_size=100,
    )
    statuses = await status_service.list_statuses(uuid.UUID(organization_id))
    return templates.TemplateResponse(
        request,
        "tasks.html",
        {
            "tasks": tasks,
            "statuses": statuses,
            "organization_id": organization_id,
            "project_id": project_id,
            "search_query": search,
        },
    )


@router.post("/organizations/{organization_id}/projects/{project_id}/tasks")
async def create_task(
    request: Request,
    organization_id: str,
    project_id: str,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
    title: Annotated[str, Form()],
    status_id: Annotated[str, Form()],
    priority: Annotated[str, Form()],
    description: Annotated[str, Form()] = "",
    _: Annotated[None, Depends(require_permission_web(Permissions.TASK_CREATE))] = None,
):
    task_service = TaskService(db)
    try:
        await task_service.create_task(
            organization_id=uuid.UUID(organization_id),
            project_id=uuid.UUID(project_id),
            status_id=uuid.UUID(status_id),
            title=title,
            description=description or None,
            priority=priority,
            parent_task_id=None,
            due_date=None,
            created_by=current_user.id,
        )
    except TaskStatusNotFoundError:
        pass  # form only offers valid statuses; this shouldn't normally trigger
    return RedirectResponse(
        url=f"/organizations/{organization_id}/projects/{project_id}/tasks",
        status_code=303,
    )


@router.get("/organizations/{organization_id}/projects/{project_id}/tasks/{task_id}")
async def task_detail(
    request: Request,
    organization_id: str,
    project_id: str,
    task_id: str,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    task_service = TaskService(db)
    comment_service = CommentService(db)
    attachment_service = AttachmentService(db)
    task = await task_service.get_task(uuid.UUID(task_id))
    assignees_with_names = await task_service.list_assignees_with_names(
        uuid.UUID(task_id)
    )
    comments_with_authors = await comment_service.list_comments_with_authors(
        uuid.UUID(task_id)
    )
    attachments = await attachment_service.list_attachments(uuid.UUID(task_id))
    return templates.TemplateResponse(
        request,
        "task_detail.html",
        {
            "task": task,
            "assignees": assignees_with_names,
            "comments": comments_with_authors,
            "attachments": attachments,
            "organization_id": organization_id,
            "current_user_id": current_user.id,
        },
    )


@router.post("/organizations/{organization_id}/tasks/{task_id}/assignees")
async def assign_task(
    request: Request,
    organization_id: str,
    task_id: str,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
    email: Annotated[str, Form()],
):
    task_service = TaskService(db)
    try:
        await task_service.assign_user(
            organization_id=uuid.UUID(organization_id),
            task_id=uuid.UUID(task_id),
            email=email,
            requesting_user_id=current_user.id,  # <-- naya
        )
    except (UserNotFoundError, UserAlreadyAssignedError, InvalidCredentialsError) as e:
        task = await task_service.get_task(uuid.UUID(task_id))
        return templates.TemplateResponse(
            request,
            "task_detail.html",
            {
                "task": task,
                "assignees": await task_service.list_assignees_with_names(
                    uuid.UUID(task_id)
                ),
                "comments": [],
                "attachments": [],
                "organization_id": organization_id,
                "current_user_id": current_user.id,
                "error": str(e),
            },
        )
    task = await task_service.get_task(uuid.UUID(task_id))
    return RedirectResponse(
        url=f"/organizations/{organization_id}/projects/{task.project_id}/tasks/{task_id}",
        status_code=303,
    )


@router.post("/organizations/{organization_id}/tasks/{task_id}/comments")
async def add_comment(
    request: Request,
    organization_id: str,
    task_id: str,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
    content: Annotated[str, Form()],
):
    comment_service = CommentService(db)
    await comment_service.create_comment(
        organization_id=uuid.UUID(organization_id),
        task_id=uuid.UUID(task_id),
        user_id=current_user.id,
        content=content,
        parent_comment_id=None,
    )
    task_service = TaskService(db)
    task = await task_service.get_task(uuid.UUID(task_id))
    return RedirectResponse(
        url=f"/organizations/{organization_id}/projects/{task.project_id}/tasks/{task_id}",
        status_code=303,
    )


@router.post("/organizations/{organization_id}/tasks/{task_id}/update")
async def update_task(
    organization_id: str,
    task_id: str,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
    title: Annotated[str, Form()],
    priority: Annotated[str, Form()],
    description: Annotated[str, Form()] = "",
    _: Annotated[None, Depends(require_permission_web(Permissions.TASK_UPDATE))] = None,
):
    task_service = TaskService(db)
    task = await task_service.update_task(
        task_id=uuid.UUID(task_id),
        title=title,
        description=description or None,
        status_id=None,
        priority=priority,
        due_date=None,
    )
    return RedirectResponse(
        url=f"/organizations/{organization_id}/projects/{task.project_id}/tasks/{task_id}",
        status_code=303,
    )


@router.post("/organizations/{organization_id}/tasks/{task_id}/delete")
async def delete_task(
    request: Request,
    organization_id: str,
    task_id: str,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    task_service = TaskService(db)
    task = await task_service.get_task(uuid.UUID(task_id))
    project_id = task.project_id
    try:
        await task_service.delete_task(
            uuid.UUID(task_id), requesting_user_id=current_user.id
        )
    except InvalidCredentialsError:
        return templates.TemplateResponse(
            request,
            "task_detail.html",
            {
                "task": task,
                "assignees": await task_service.list_assignees_with_names(
                    uuid.UUID(task_id)
                ),
                "comments": [],
                "attachments": [],
                "organization_id": organization_id,
                "current_user_id": current_user.id,
                "error": "Only the Project Manager can delete tasks",
            },
        )
    return RedirectResponse(
        url=f"/organizations/{organization_id}/projects/{project_id}/tasks",
        status_code=303,
    )


@router.post(
    "/organizations/{organization_id}/tasks/{task_id}/comments/{comment_id}/delete"
)
async def delete_comment(
    organization_id: str,
    task_id: str,
    comment_id: str,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    comment_service = CommentService(db)
    try:
        await comment_service.delete_comment(
            comment_id=uuid.UUID(comment_id), requesting_user_id=current_user.id
        )
    except (CommentNotFoundError, NotCommentOwnerError):
        pass
    task_service = TaskService(db)
    task = await task_service.get_task(uuid.UUID(task_id))
    return RedirectResponse(
        url=f"/organizations/{organization_id}/projects/{task.project_id}/tasks/{task_id}",
        status_code=303,
    )


@router.post("/organizations/{organization_id}/task-statuses")
async def create_task_status(
    organization_id: str,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
    name: Annotated[str, Form()],
    color: Annotated[str, Form()],
    position: Annotated[int, Form()],
    _: Annotated[
        None, Depends(require_permission_web(Permissions.PROJECT_MANAGE_MEMBERS))
    ],
):
    status_service = TaskStatusService(db)
    try:
        await status_service.create_status(
            organization_id=uuid.UUID(organization_id),
            name=name,
            color=color,
            position=position,
        )
    except TaskStatusAlreadyExistsError:
        pass  # silently ignore for now — simple form, not critical path
    # Redirect back to the project's task list. Since we don't have
    # project_id here, redirect to organizations list as a safe fallback.
    return RedirectResponse(url="/organizations", status_code=303)


@router.post("/organizations/{organization_id}/tasks/{task_id}/attachments")
async def add_attachment(
    organization_id: str,
    task_id: str,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
    original_filename: Annotated[str, Form()],
    file_url: Annotated[str, Form()],
    mime_type: Annotated[str, Form()],
):
    attachment_service = AttachmentService(db)
    await attachment_service.create_attachment(
        organization_id=uuid.UUID(organization_id),
        task_id=uuid.UUID(task_id),
        uploaded_by=current_user.id,
        original_filename=original_filename,
        mime_type=mime_type,
        size=0,
        file_url=file_url,
    )
    task_service = TaskService(db)
    task = await task_service.get_task(uuid.UUID(task_id))
    return RedirectResponse(
        url=f"/organizations/{organization_id}/projects/{task.project_id}/tasks/{task_id}",
        status_code=303,
    )
