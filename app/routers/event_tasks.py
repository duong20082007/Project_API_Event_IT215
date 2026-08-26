from fastapi import APIRouter, Depends, Request, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db
from app.schemas.response import APIResponse
from app.schemas.event_task import EventTaskCreate, EventTaskUpdate
from app.models.user import User
from app.dependencies.auth_deps import get_current_user
import app.services.event_task_service as task_svc

router = APIRouter(tags=["Event Tasks"])

@router.post("/events/{id}/event-tasks", response_model=APIResponse)
def create_event_task(id: int, task_in: EventTaskCreate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = task_svc.create_task(db=db, event_id=id, task_in=task_in, current_user_id=current_user.id)
    
    task_data = {
        "id": task.id, 
        "event_id": task.event_id, 
        "title": task.title, 
        "description": task.description, 
        "status": task.status, 
        "priority": task.priority, 
        "assignee_id": task.assignee_id, 
        "due_date": task.due_date
    }
    
    return APIResponse(
        statusCode=status.HTTP_201_CREATED, 
        message="Tạo công việc thành công", 
        data=task_data, 
        path=str(request.url.path)
    )

@router.get("/events/{id}/event-tasks", response_model=APIResponse)
def get_event_tasks(
    id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
    search: Optional[str] = Query(None), 
    status_filter: Optional[str] = Query(None, alias="status"),
    priority: Optional[str] = Query(None), 
    assignee_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1), 
    size: int = Query(10, ge=1, le=100),
    sort_by: str = Query("created_at"), 
    order: str = Query("desc", regex="^(asc|desc)$")
):
    tasks, total = task_svc.get_event_tasks(
        db, id, current_user.id, search, status_filter, priority, assignee_id, page, size, sort_by, order
    )
    
    data_list = [{
        "id": t.id, 
        "title": t.title, 
        "status": t.status, 
        "priority": t.priority,
        "assignee_id": t.assignee_id, 
        "due_date": t.due_date, 
        "created_at": t.created_at
    } for t in tasks]
    
    return APIResponse(
        statusCode=status.HTTP_200_OK, 
        message="Lấy danh sách công việc thành công",
        data={"items": data_list, "total": total, "page": page, "size": size},
        path=str(request.url.path)
    )

@router.get("/event-tasks/{id}", response_model=APIResponse)
def get_task_detail(id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = task_svc.get_task_detail(db, task_id=id, current_user_id=current_user.id)
    
    task_data = {
        "id": task.id, 
        "event_id": task.event_id, 
        "title": task.title, 
        "description": task.description, 
        "status": task.status, 
        "priority": task.priority, 
        "assignee_id": task.assignee_id, 
        "due_date": task.due_date, 
        "created_at": task.created_at
    }
    
    return APIResponse(
        statusCode=status.HTTP_200_OK, 
        message="Lấy chi tiết công việc thành công", 
        data=task_data, 
        path=str(request.url.path)
    )

@router.patch("/event-tasks/{id}", response_model=APIResponse)
def update_task(id: int, task_in: EventTaskUpdate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = task_svc.update_task(db, task_id=id, task_in=task_in, current_user_id=current_user.id)
    
    task_data = {
        "id": task.id, 
        "title": task.title, 
        "status": task.status, 
        "priority": task.priority, 
        "assignee_id": task.assignee_id
    }
    
    return APIResponse(
        statusCode=status.HTTP_200_OK, 
        message="Cập nhật công việc thành công", 
        data=task_data, 
        path=str(request.url.path)
    )

@router.delete("/event-tasks/{id}", response_model=APIResponse)
def delete_task(id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task_svc.delete_task(db, task_id=id, current_user_id=current_user.id)
    
    return APIResponse(
        statusCode=status.HTTP_200_OK, 
        message="Xóa công việc thành công", 
        data=None, 
        path=str(request.url.path)
    )