from sqlalchemy.orm import Session
from fastapi import Request, HTTPException, status
from typing import Optional
from datetime import datetime

from app.schemas.event import EventCreate, EventUpdate
from app.schemas.event_staff import EventStaffCreate
from app.models.event import Event, EventStaff
from app.models.user import User

import logging

logging.basicConfig(
    filename="app.log",
    filemode="a",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s',
    encoding='utf-8'
)

def get_event_or_404(db: Session, event_id: int):
    event = db.query(Event).filter(Event.id == event_id, Event.is_deleted == False).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sự kiện không tồn tại hoặc đã bị xóa.")
    return event

def verify_owner(event: Event, user_id: int):
    if event.owner_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bạn không phải là chủ phòng (OWNER).")

def check_is_member_or_owner(db: Session, event_id: int, user_id: int):
    is_member = db.query(EventStaff).filter(EventStaff.event_id == event_id, EventStaff.user_id == user_id).first()
    if not is_member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bạn không có quyền truy cập.")

def create_event(db: Session, event_in: EventCreate, current_user_id: int):
    if not event_in.name or len(event_in.name.strip()) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tên sự kiện không được để trống.")
        
    new_event = Event(
        name=event_in.name.strip(),
        description=event_in.description,
        owner_id=current_user_id
    )
    
    try:
        db.add(new_event)
        db.commit()
        db.refresh(new_event)
        
        owner_staff = EventStaff(event_id=new_event.id, user_id=current_user_id, role="OWNER")
        db.add(owner_staff)
        db.commit()
        
        logging.info(f"User ID {current_user_id} đã TẠO sự kiện '{new_event.name}' (ID: {new_event.id})")
        return new_event
    except Exception as e:
        db.rollback()
        logging.error(f"Lỗi khi tạo sự kiện: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

def get_my_events(db: Session, current_user_id: int, search: Optional[str] = None):
    query = db.query(Event).join(EventStaff, Event.id == EventStaff.event_id).filter(
        EventStaff.user_id == current_user_id,
        Event.is_deleted == False
    )
    if search:
        query = query.filter(Event.name.ilike(f"%{search}%"))
    return query.all()

def update_event(db: Session, event_id: int, event_in: EventUpdate, current_user_id: int):
    event = get_event_or_404(db, event_id)
    verify_owner(event, current_user_id)
    
    try:
        if event_in.name is not None:
            event.name = event_in.name.strip()
        if event_in.description is not None:
            event.description = event_in.description
            
        db.commit()
        db.refresh(event)
        
        logging.info(f"User ID {current_user_id} đã CẬP NHẬT sự kiện ID: {event.id}")
        return event
    except Exception as e:
        db.rollback()
        logging.error(f"Lỗi khi cập nhật sự kiện {event_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

def delete_event(db: Session, event_id: int, current_user_id: int):
    event = get_event_or_404(db, event_id)
    verify_owner(event, current_user_id)
    
    try:
        event.is_deleted = True
        event.deleted_at = datetime.now()
        db.commit()
        
        logging.info(f"User ID {current_user_id} đã XÓA (Soft Delete) sự kiện ID: {event.id}")
    except Exception as e:
        db.rollback()
        logging.error(f"Lỗi khi xóa sự kiện {event_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

def add_member(db: Session, event_id: int, member_in: EventStaffCreate, current_user_id: int):
    event = get_event_or_404(db, event_id)
    verify_owner(event, current_user_id)
    
    user_to_add = db.query(User).filter(User.id == member_in.user_id).first()
    if not user_to_add:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại.")
        
    if db.query(EventStaff).filter(EventStaff.event_id == event_id, EventStaff.user_id == member_in.user_id).first():
        raise HTTPException(status_code=400, detail="Đã là thành viên.")
        
    new_staff = EventStaff(event_id=event_id, user_id=member_in.user_id, role=member_in.role)
    
    try:
        db.add(new_staff)
        db.commit()
        db.refresh(new_staff)
        
        logging.info(f"User ID {current_user_id} đã THÊM thành viên {member_in.user_id} (Quyền: {member_in.role}) vào sự kiện ID: {event_id}")
        return new_staff
    except Exception as e:
        db.rollback()
        logging.error(f"Lỗi khi thêm thành viên vào sự kiện {event_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def remove_member(db: Session, event_id: int, user_id_to_remove: int, current_user_id: int):
    event = get_event_or_404(db, event_id)
    verify_owner(event, current_user_id)
    
    if event.owner_id == user_id_to_remove:
        raise HTTPException(status_code=400, detail="Không thể xóa OWNER.")
        
    staff = db.query(EventStaff).filter(EventStaff.event_id == event_id, EventStaff.user_id == user_id_to_remove).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Không có thành viên này.")
        
    try:
        db.delete(staff)
        db.commit()
        
        logging.info(f"User ID {current_user_id} đã XÓA thành viên {user_id_to_remove} khỏi sự kiện ID: {event_id}")
    except Exception as e:
        db.rollback()
        logging.error(f"Lỗi khi xóa thành viên khỏi sự kiện {event_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def get_members(db: Session, event_id: int, current_user_id: int):
    get_event_or_404(db, event_id)
    check_is_member_or_owner(db, event_id, current_user_id)
    return db.query(EventStaff).filter(EventStaff.event_id == event_id).all()