from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class EventBase(BaseModel):
    name: str
    description: Optional[str] = None

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class EventResponse(EventBase):
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True