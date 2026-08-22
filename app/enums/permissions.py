class Permissions:
    # Organization
    ORG_MANAGE_MEMBERS = "organization:manage_members"
    ORG_MANAGE_SETTINGS = "organization:manage_settings"
    ORG_DELETE = "organization:delete"

    # Team
    TEAM_CREATE = "team:create"
    TEAM_MANAGE_MEMBERS = "team:manage_members"
    TEAM_DELETE = "team:delete"

    # Project
    PROJECT_CREATE = "project:create"
    PROJECT_MANAGE_MEMBERS = "project:manage_members"
    PROJECT_DELETE = "project:delete"

    # Task
    TASK_CREATE = "task:create"
    TASK_UPDATE = "task:update"
    TASK_DELETE = "task:delete"
    TASK_ASSIGN = "task:assign"

    @classmethod
    def all_permissions(cls) -> list[str]:
        """Used by the seed script to insert every permission into the DB."""
        return [
            value
            for key, value in vars(cls).items()
            if not key.startswith("_") and isinstance(value, str)
        ]
