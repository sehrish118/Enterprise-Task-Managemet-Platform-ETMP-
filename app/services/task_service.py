# import uuid
# from datetime import datetime

# from sqlalchemy.ext.asyncio import AsyncSession

# from app.core.exceptions import (
#     TaskNotFoundError,
#     TaskStatusNotFoundError,
#     UserAlreadyAssignedError,
#     UserNotFoundError,
#     InvalidCredentialsError,
# )
# from app.models.task import Task
# from app.models.task_assignee import TaskAssignee
# from app.repositories.task_repository import TaskRepository
# from app.repositories.task_status_repository import TaskStatusRepository
# from app.repositories.user_repository import UserRepository
# from app.repositories.project_repository import ProjectRepository
# from app.models.project_member import ProjectMemberRole


# class TaskService:
#     def __init__(self, session: AsyncSession) -> None:
#         self.session = session
#         self.task_repo = TaskRepository(session)
#         self.status_repo = TaskStatusRepository(session)
#         self.user_repo = UserRepository(session)
#         self.project_repo = ProjectRepository(session)

#     async def create_task(
#         self,
#         *,
#         organization_id: uuid.UUID,
#         project_id: uuid.UUID,
#         status_id: uuid.UUID,
#         title: str,
#         description: str | None,
#         priority: str,
#         parent_task_id: uuid.UUID | None,
#         due_date: datetime | None,
#         created_by: uuid.UUID,
#     ) -> Task:
#         status = await self.status_repo.get_by_id(status_id)
#         if status is None:
#             raise TaskStatusNotFoundError(f"Task status {status_id} not found")

#         task = await self.task_repo.create(
#             organization_id=organization_id,
#             project_id=project_id,
#             status_id=status_id,
#             title=title,
#             description=description,
#             priority=priority,
#             parent_task_id=parent_task_id,
#             due_date=due_date,
#             created_by=created_by,
#         )
#         await self.session.commit()
#         return task

#     async def get_task(self, task_id: uuid.UUID) -> Task:
#         task = await self.task_repo.get_by_id(task_id)
#         if task is None:
#             raise TaskNotFoundError(f"Task {task_id} not found")
#         return task

#     async def update_task(
#         self,
#         *,
#         task_id: uuid.UUID,
#         title: str | None,
#         description: str | None,
#         status_id: uuid.UUID | None,
#         priority: str | None,
#         due_date: datetime | None,
#     ) -> Task:
#         task = await self.get_task(task_id)

#         if status_id is not None:
#             status = await self.status_repo.get_by_id(status_id)
#             if status is None:
#                 raise TaskStatusNotFoundError(f"Task status {status_id} not found")

#         task = await self.task_repo.update(
#             task,
#             title=title,
#             description=description,
#             status_id=status_id,
#             priority=priority,
#             due_date=due_date,
#         )
#         await self.session.commit()
#         return task

#     async def delete_task(
#         self, task_id: uuid.UUID, *, requesting_user_id: uuid.UUID
#     ) -> None:
#         task = await self.get_task(task_id)

#         requester_role = await self.project_repo.get_member_role(
#             project_id=task.project_id, user_id=requesting_user_id
#         )
#         if requester_role != ProjectMemberRole.PROJECT_MANAGER:
#             from app.core.exceptions import InvalidCredentialsError

#             raise InvalidCredentialsError(
#                 "Only the Project Manager can delete tasks in this project"
#             )

#         await self.task_repo.soft_delete(task)
#         await self.session.commit()

#     async def list_tasks(
#         self,
#         project_id: uuid.UUID,
#         *,
#         status_id: uuid.UUID | None = None,
#         priority: str | None = None,
#         search: str | None = None,
#         page: int = 1,
#         page_size: int = 20,
#     ) -> tuple[list[Task], int]:
#         offset = (page - 1) * page_size
#         return await self.task_repo.list_by_project(
#             project_id,
#             status_id=status_id,
#             priority=priority,
#             search=search,
#             offset=offset,
#             limit=page_size,
#         )

#     async def assign_user(
#         self,
#         *,
#         organization_id: uuid.UUID,
#         task_id: uuid.UUID,
#         email: str,
#         requesting_user_id: uuid.UUID,
#     ) -> TaskAssignee:
#         task = await self.get_task(task_id)

#         # Only the Project Manager may assign tasks — not even to themselves.
#         requester_role = await self.project_repo.get_member_role(
#             project_id=task.project_id, user_id=requesting_user_id
#         )
#         if requester_role != ProjectMemberRole.PROJECT_MANAGER:
#             from app.core.exceptions import InvalidCredentialsError

#             raise InvalidCredentialsError("Only the Project Manager can assign tasks")

#         user = await self.user_repo.get_by_email(email)
#         if user is None:
#             raise UserNotFoundError(f"No user registered with email '{email}'")

#         existing = await self.task_repo.get_assignment(task_id=task_id, user_id=user.id)
#         if existing is not None:
#             raise UserAlreadyAssignedError(
#                 f"'{email}' is already assigned to this task"
#             )

#         assignee = await self.task_repo.assign_user(
#             organization_id=organization_id, task_id=task_id, user_id=user.id
#         )

#         from app.services.notification_service import NotificationService
#         from app.services.activity_log_service import ActivityLogService

#         await NotificationService(self.session).notify(
#             organization_id=organization_id,
#             user_id=user.id,
#             type_code="TASK_ASSIGNED",
#             title="You were assigned a task",
#             message=f"You were assigned to task: {task.title}",
#             entity_type="task",
#             entity_id=task_id,
#         )
#         await ActivityLogService(self.session).log(
#             organization_id=organization_id,
#             user_id=user.id,
#             action="task_assigned",
#             entity_type="task",
#             entity_id=task_id,
#         )

#         await self.session.commit()
#         return assignee

#     async def list_assignees(self, task_id: uuid.UUID) -> list[TaskAssignee]:
#         await self.get_task(task_id)
#         return await self.task_repo.list_assignees(task_id)

#     async def list_assignees_with_names(self, task_id: uuid.UUID) -> list[tuple]:
#         await self.get_task(task_id)
#         return await self.task_repo.list_assignees_with_names(task_id)

#     async def unassign_user(
#         self,
#         *,
#         task_id: uuid.UUID,
#         user_id: uuid.UUID,
#         requesting_user_id: uuid.UUID,
#     ) -> None:
#         task = await self.get_task(task_id)

#         requester_role = await self.project_repo.get_member_role(
#             project_id=task.project_id, user_id=requesting_user_id
#         )
#         if requester_role != ProjectMemberRole.PROJECT_MANAGER:
#             raise InvalidCredentialsError("Only the Project Manager can unassign users")

#         removed = await self.task_repo.unassign_user(task_id=task_id, user_id=user_id)
#         if not removed:
#             raise UserNotFoundError("User assignment not found for this task")

#         await self.session.commit()


import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    InvalidCredentialsError,
    TaskNotFoundError,
    TaskStatusNotFoundError,
    UserAlreadyAssignedError,
    UserNotFoundError,
)
from app.rag.tasks import embed_entity_task
from app.rag.tasks import embed_entity_task, delete_embedding_task
from app.models.project_member import ProjectMemberRole
from app.models.task import Task
from app.models.task_assignee import TaskAssignee
from app.repositories.project_repository import ProjectRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.task_status_repository import TaskStatusRepository
from app.repositories.user_repository import UserRepository
from app.services.activity_log_service import ActivityLogService
from app.services.notification_service import NotificationService


class TaskService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.task_repo = TaskRepository(session)
        self.status_repo = TaskStatusRepository(session)
        self.user_repo = UserRepository(session)
        self.project_repo = ProjectRepository(session)

    async def create_task(
        self,
        *,
        organization_id: uuid.UUID,
        project_id: uuid.UUID,
        status_id: uuid.UUID,
        title: str,
        description: str | None,
        priority: str,
        parent_task_id: uuid.UUID | None,
        due_date: datetime | None,
        created_by: uuid.UUID,
    ) -> Task:
        status = await self.status_repo.get_by_id(status_id)
        if status is None:
            raise TaskStatusNotFoundError(f"Task status {status_id} not found")

        task = await self.task_repo.create(
            organization_id=organization_id,
            project_id=project_id,
            status_id=status_id,
            title=title,
            description=description,
            priority=priority,
            parent_task_id=parent_task_id,
            due_date=due_date,
            created_by=created_by,
        )
        await self.session.commit()
        embed_entity_task.delay(
            organization_id=str(organization_id),
            project_id=str(project_id),
            entity_type="task",
            entity_id=str(task.id),
            content=f"{title}\n{description or ''}".strip(),
        )

        return task

    async def get_task(self, task_id: uuid.UUID) -> Task:
        task = await self.task_repo.get_by_id(task_id)
        if task is None:
            raise TaskNotFoundError(f"Task {task_id} not found")
        return task

    async def update_task(
        self,
        *,
        task_id: uuid.UUID,
        title: str | None,
        description: str | None,
        status_id: uuid.UUID | None,
        priority: str | None,
        due_date: datetime | None,
    ) -> Task:
        task = await self.get_task(task_id)

        if status_id is not None:
            status = await self.status_repo.get_by_id(status_id)
            if status is None:
                raise TaskStatusNotFoundError(f"Task status {status_id} not found")

        task = await self.task_repo.update(
            task,
            title=title,
            description=description,
            status_id=status_id,
            priority=priority,
            due_date=due_date,
        )
        await self.session.commit()
        embed_entity_task.delay(
            organization_id=str(task.organization_id),
            project_id=str(task.project_id),
            entity_type="task",
            entity_id=str(task.id),
            content=f"{task.title}\n{task.description or ''}".strip(),
        )
        return task

    async def delete_task(
        self, task_id: uuid.UUID, *, requesting_user_id: uuid.UUID
    ) -> None:
        task = await self.get_task(task_id)

        requester_role = await self.project_repo.get_member_role(
            project_id=task.project_id, user_id=requesting_user_id
        )
        if requester_role != ProjectMemberRole.PROJECT_MANAGER:
            raise InvalidCredentialsError(
                "Only the Project Manager can delete tasks in this project"
            )

        await self.task_repo.soft_delete(task)
        await self.session.commit()
        delete_embedding_task.delay(entity_type="task", entity_id=str(task_id))

    async def list_tasks(
        self,
        project_id: uuid.UUID,
        *,
        status_id: uuid.UUID | None = None,
        priority: str | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Task], int]:
        offset = (page - 1) * page_size
        return await self.task_repo.list_by_project(
            project_id,
            status_id=status_id,
            priority=priority,
            search=search,
            offset=offset,
            limit=page_size,
        )

    async def assign_user(
        self,
        *,
        organization_id: uuid.UUID,
        task_id: uuid.UUID,
        email: str,
        requesting_user_id: uuid.UUID,
    ) -> TaskAssignee:
        task = await self.get_task(task_id)

        requester_role = await self.project_repo.get_member_role(
            project_id=task.project_id, user_id=requesting_user_id
        )
        if requester_role != ProjectMemberRole.PROJECT_MANAGER:
            raise InvalidCredentialsError("Only the Project Manager can assign tasks")

        user = await self.user_repo.get_by_email(email)
        if user is None:
            raise UserNotFoundError(f"No user registered with email '{email}'")

        existing = await self.task_repo.get_assignment(task_id=task_id, user_id=user.id)
        if existing is not None:
            raise UserAlreadyAssignedError(
                f"'{email}' is already assigned to this task"
            )

        assignee = await self.task_repo.assign_user(
            organization_id=organization_id, task_id=task_id, user_id=user.id
        )

        await NotificationService(self.session).notify(
            organization_id=organization_id,
            user_id=user.id,
            type_code="TASK_ASSIGNED",
            title="You were assigned a task",
            message=f"You were assigned to task: {task.title}",
            entity_type="task",
            entity_id=task_id,
        )
        await ActivityLogService(self.session).log(
            organization_id=organization_id,
            user_id=user.id,
            action="task_assigned",
            entity_type="task",
            entity_id=task_id,
        )

        await self.session.commit()
        return assignee

    async def list_assignees(self, task_id: uuid.UUID) -> list[TaskAssignee]:
        await self.get_task(task_id)
        return await self.task_repo.list_assignees(task_id)

    async def list_assignees_with_names(self, task_id: uuid.UUID) -> list[tuple]:
        await self.get_task(task_id)
        return await self.task_repo.list_assignees_with_names(task_id)

    async def unassign_user(
        self,
        *,
        task_id: uuid.UUID,
        user_id: uuid.UUID,
        requesting_user_id: uuid.UUID,
    ) -> None:
        task = await self.get_task(task_id)

        requester_role = await self.project_repo.get_member_role(
            project_id=task.project_id, user_id=requesting_user_id
        )
        if requester_role != ProjectMemberRole.PROJECT_MANAGER:
            raise InvalidCredentialsError("Only the Project Manager can unassign users")

        removed = await self.task_repo.unassign_user(task_id=task_id, user_id=user_id)
        if not removed:
            raise UserNotFoundError("User assignment not found for this task")

        await self.session.commit()
