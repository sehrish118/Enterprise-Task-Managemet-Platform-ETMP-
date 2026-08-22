import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.dashboard_repository import DashboardRepository
from app.schemas.dashboard import MyDashboard, MyTaskSummary, OrganizationDashboard


class DashboardService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = DashboardRepository(session)

    async def get_my_dashboard(self, user_id: uuid.UUID) -> MyDashboard:
        assigned_count = await self.repo.count_assigned_tasks(user_id)
        overdue_count = await self.repo.count_overdue_tasks(user_id)
        unread_count = await self.repo.count_unread_notifications(user_id)
        recent = await self.repo.recent_assigned_tasks(user_id)

        return MyDashboard(
            assigned_tasks_count=assigned_count,
            overdue_tasks_count=overdue_count,
            unread_notifications_count=unread_count,
            recent_tasks=[
                MyTaskSummary(
                    id=t.id,
                    title=t.title,
                    priority=t.priority.value,
                    due_date=t.due_date,
                    project_id=t.project_id,
                    status_id=t.status_id,
                )
                for t in recent
            ],
        )

    async def get_organization_dashboard(
        self, organization_id: uuid.UUID
    ) -> OrganizationDashboard:
        total_projects = await self.repo.count_projects(organization_id)
        active_projects = await self.repo.count_active_projects(organization_id)
        total_tasks = await self.repo.count_tasks(organization_id)
        total_members = await self.repo.count_members(organization_id)
        priority_breakdown = await self.repo.tasks_by_priority(organization_id)

        return OrganizationDashboard(
            total_projects=total_projects,
            active_projects=active_projects,
            total_tasks=total_tasks,
            total_members=total_members,
            tasks_by_priority=priority_breakdown,
        )
