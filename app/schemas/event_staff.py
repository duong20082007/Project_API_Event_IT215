from pydantic import BaseModel
from datetime import datetime

class EventStaffBase(BaseModel):
    role: str

class EventStaffCreate(EventStaffBase):
    user_id: int

class EventStaffResponse(EventStaffBase):
    event_id: int
    user_id: int
    joined_at: datetime

    class Config:
        from_attributes = True