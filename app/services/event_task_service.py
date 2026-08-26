from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional
from sqlalchemy import desc, asc
import logging

from app.models.event import EventStaff
from app.models.event_task import EventTask 
from app.schemas.event_task import EventTaskCreate, EventTaskUpdate

def get_user_role(db: Session, event_id: int, user_id: int) -> str:
    staff = db.query(EventStaff).filter(EventStaff.event_id == event_id, EventStaff.user_id == user_id).first()
    if not staff:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bạn không phải thành viên sự kiện này.")
    return staff.role

def verify_assignee_is_member(db: Session, event_id: int, assignee_id: int):
    staff = db.query(EventStaff).filter(EventStaff.event_id == event_id, EventStaff.user_id == assignee_id).first()
    if not staff:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Người được giao việc phải thuộc ban tổ chức sự kiện.")

def get_task_or_404(db: Session, task_id: int):
    task = db.query(EventTask).filter(EventTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Công việc không tồn tại.")
    return task

def create_task(db: Session, event_id: int, task_in: EventTaskCreate, current_user_id: int):
    get_user_role(db, event_id, current_user_id)
    
    if task_in.assignee_id:
        verify_assignee_is_member(db, event_id, task_in.assignee_id)
        
    new_task = EventTask(
        event_id=event_id,
        title=task_in.title.strip(),
        description=task_in.description,
        status=task_in.status,
        priority=task_in.priority,
        assignee_id=task_in.assignee_id,
        due_date=task_in.due_date
    )
    
    try:
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        logging.info(f"User ID {current_user_id} đã TẠO task '{new_task.title}' trong sự kiện ID: {event_id}")
        return new_task
    except Exception as e:
        db.rollback()
        logging.error(f"Lỗi tạo task: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

def get_event_tasks(
    db: Session, event_id: int, current_user_id: int,
    search: Optional[str] = None, status_filter: Optional[str] = None,
    priority: Optional[str] = None, assignee_id: Optional[int] = None,
    page: int = 1, size: int = 10, sort_by: str = "created_at", order: str = "desc"
):
    get_user_role(db, event_id, current_user_id)
    
    query = db.query(EventTask).filter(EventTask.event_id == event_id)
    
    if search:
        query = query.filter(EventTask.title.ilike(f"%{search}%"))
    if status_filter:
        query = query.filter(EventTask.status == status_filter)
    if priority:
        query = query.filter(EventTask.priority == priority)
    if assignee_id:
        query = query.filter(EventTask.assignee_id == assignee_id)
        
    if hasattr(EventTask, sort_by):
        column = getattr(EventTask, sort_by)
        query = query.order_by(desc(column) if order == "desc" else asc(column))
        
    total = query.count()
    offset = (page - 1) * size
    tasks = query.offset(offset).limit(size).all()
    
    return tasks, total

def get_task_detail(db: Session, task_id: int, current_user_id: int):
    task = get_task_or_404(db, task_id)
    get_user_role(db, task.event_id, current_user_id) 
    return task

def update_task(db: Session, task_id: int, task_in: EventTaskUpdate, current_user_id: int):
    task = get_task_or_404(db, task_id)
    role = get_user_role(db, task.event_id, current_user_id)
    
    is_owner = (role == "OWNER")
    is_assignee = (task.assignee_id == current_user_id)
    
    if not (is_owner or is_assignee):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Chỉ Owner hoặc người được giao việc mới được sửa.")
        
    if is_assignee and not is_owner:
        if any([task_in.title is not None, task_in.priority is not None, task_in.assignee_id is not None, task_in.due_date is not None]):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Người thực hiện chỉ được phép cập nhật tiến độ (status).")

    if task_in.assignee_id is not None:
        verify_assignee_is_member(db, task.event_id, task_in.assignee_id)

    update_data = task_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)
        
    try:
        db.commit()
        db.refresh(task)
        logging.info(f"User ID {current_user_id} CẬP NHẬT task ID: {task_id}")
        return task
    except Exception as e:
        db.rollback()
        logging.error(f"Lỗi cập nhật task: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

def delete_task(db: Session, task_id: int, current_user_id: int):
    task = get_task_or_404(db, task_id)
    role = get_user_role(db, task.event_id, current_user_id)
    
    if role != "OWNER":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Chỉ Owner mới có quyền xóa công việc.")
        
    try:
        db.delete(task)
        db.commit()
        logging.info(f"User ID {current_user_id} XÓA task ID: {task_id}")
    except Exception as e:
        db.rollback()
        logging.error(f"Lỗi xóa task: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))