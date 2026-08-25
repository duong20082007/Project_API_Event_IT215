from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)

    owner = relationship("User", back_populates="events_owned")
    staff_members = relationship("EventStaff", back_populates="event")
    tasks = relationship("EventTask", back_populates="event")

class EventStaff(Base):
    __tablename__ = "event_staff"

    event_id = Column(Integer, ForeignKey("events.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    role = Column(String(50), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    event = relationship("Event", back_populates="staff_members")
    user = relationship("User", back_populates="staff_roles")
    