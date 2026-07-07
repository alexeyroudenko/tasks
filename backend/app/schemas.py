import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    name: str


class ProjectIn(BaseModel):
    name: str
    description: str | None = None
    icon: str = "clipboard-list"
    user_id: uuid.UUID | None = None


class ProjectPatch(BaseModel):
    name: str | None = None
    description: str | None = None
    icon: str | None = None
    user_id: uuid.UUID | None = None


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None
    icon: str
    user_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime


class TaskIn(BaseModel):
    title: str
    description: str | None = None
    deadline: date | None = None
    status: str = "todo"
    type: str = "task"
    user_id: str | None = None


class TaskPatch(BaseModel):
    title: str | None = None
    description: str | None = None
    deadline: date | None = None
    status: str | None = None
    type: str | None = None
    user_id: str | None = None


class TaskOut(BaseModel):
    id: str
    title: str
    description: str | None = None
    deadline: str | None = None
    status: str
    type: str
    user_id: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    relationships: dict[str, list["TaskRef"]] | None = None


class TaskRef(BaseModel):
    id: str
    title: str


class RelationshipIn(BaseModel):
    from_id: str
    type: str
    to_id: str
