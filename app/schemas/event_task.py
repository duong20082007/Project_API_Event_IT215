from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class EventTaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = "TODO"
    priority: Optional[str] = "NORMAL"
    due_date: Optional[datetime] = None

class EventTaskCreate(EventTaskBase):
    assignee_id: Optional[int] = None

class EventTaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assignee_id: Optional[int] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None

class EventTaskResponse(EventTaskBase):
    id: int
    event_id: int
    assignee_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True