"""Pydantic schemas for Organization — request/response validation."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class OrganizationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    slug: str = Field(
        min_length=1, max_length=100, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
    )


class OrganizationUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)


class OrganizationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    created_at: datetime


class AddMemberRequest(BaseModel):
    email: EmailStr
    role_name: str = Field(description="One of: Owner, Admin, Member")
