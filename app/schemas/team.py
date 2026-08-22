import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TeamCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)


class TeamUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)


class TeamRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    created_at: datetime


class AddTeamMemberRequest(BaseModel):
    email: str
    role: str = Field(default="MEMBER", description="MEMBER or TEAM_LEAD")


class TeamMemberRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    user_id: uuid.UUID
    user_full_name: str
    role: str


class InviteResponse(BaseModel):
    message: str
    invite_link: str | None = None
