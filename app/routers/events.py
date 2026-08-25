from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db
from app.schemas.event import EventCreate, EventUpdate
from app.schemas.event_staff import EventStaffCreate
from app.schemas.response import APIResponse
from app.models.user import User
from app.dependencies.auth_deps import get_current_user
import app.services.event_service as event_svc

router = APIRouter(prefix="/events", tags=["Events"])

@router.post("", response_model=APIResponse)
def create_event(event_in: EventCreate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_event = event_svc.create_event(db=db, event_in=event_in, current_user_id=current_user.id)
    
    event_data = {
        "id": new_event.id,
        "name": new_event.name,
        "description": new_event.description,
        "owner_id": new_event.owner_id,
        "created_at": new_event.created_at
    }
    
    return APIResponse(
        statusCode=status.HTTP_201_CREATED,
        message="Tạo sự kiện thành công",
        data=event_data,
        path=str(request.url.path)
    )

@router.get("", response_model=APIResponse)
def get_events(request: Request, search: Optional[str] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    events = event_svc.get_my_events(db=db, current_user_id=current_user.id, search=search)
    
    events_data_list = [
        {
            "id": e.id,
            "name": e.name,
            "description": e.description,
            "owner_id": e.owner_id,
            "created_at": e.created_at
        } for e in events
    ]
    
    return APIResponse(
        statusCode=status.HTTP_200_OK,
        message="Lấy danh sách sự kiện thành công",
        data=events_data_list,
        path=str(request.url.path)
    )

@router.get("/{id}", response_model=APIResponse)
def get_event_detail(id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    event_svc.check_is_member_or_owner(db=db, event_id=id, user_id=current_user.id)
    event = event_svc.get_event_or_404(db=db, event_id=id)
    
    event_data = {
        "id": event.id,
        "name": event.name,
        "description": event.description,
        "owner_id": event.owner_id,
        "created_at": event.created_at
    }
    
    return APIResponse(
        statusCode=status.HTTP_200_OK,
        message="Lấy thông tin sự kiện thành công",
        data=event_data,
        path=str(request.url.path)
    )

@router.put("/{id}", response_model=APIResponse)
def update_event(id: int, event_in: EventUpdate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    updated_event = event_svc.update_event(db=db, event_id=id, event_in=event_in, current_user_id=current_user.id)
    
    event_data = {
        "id": updated_event.id,
        "name": updated_event.name,
        "description": updated_event.description,
        "owner_id": updated_event.owner_id,
        "created_at": updated_event.created_at
    }
    
    return APIResponse(
        statusCode=status.HTTP_200_OK,
        message="Cập nhật sự kiện thành công",
        data=event_data,
        path=str(request.url.path)
    )

@router.delete("/{id}", response_model=APIResponse)
def delete_event(id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    event_svc.delete_event(db=db, event_id=id, current_user_id=current_user.id)
    
    return APIResponse(
        statusCode=status.HTTP_200_OK,
        message="Xóa sự kiện thành công",
        data=None,
        path=str(request.url.path)
    )

@router.post("/{id}/members", response_model=APIResponse)
def add_event_member(id: int, member_in: EventStaffCreate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_member = event_svc.add_member(db=db, event_id=id, member_in=member_in, current_user_id=current_user.id)
    
    member_data = {
        "event_id": new_member.event_id,
        "user_id": new_member.user_id,
        "role": new_member.role,
        "joined_at": new_member.joined_at
    }
    
    return APIResponse(
        statusCode=status.HTTP_201_CREATED,
        message="Thêm thành viên thành công",
        data=member_data,
        path=str(request.url.path)
    )

@router.delete("/{id}/members/{user_id}", response_model=APIResponse)
def remove_event_member(id: int, user_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    event_svc.remove_member(db=db, event_id=id, user_id_to_remove=user_id, current_user_id=current_user.id)
    
    return APIResponse(
        statusCode=status.HTTP_200_OK,
        message="Xóa thành viên thành công",
        data=None,
        path=str(request.url.path)
    )

@router.get("/{id}/members", response_model=APIResponse)
def get_event_members(id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    members = event_svc.get_members(db=db, event_id=id, current_user_id=current_user.id)
    
    members_data_list = [
        {
            "event_id": m.event_id,
            "user_id": m.user_id,
            "role": m.role,
            "joined_at": m.joined_at
        } for m in members
    ]
    
    return APIResponse(
        statusCode=status.HTTP_200_OK,
        message="Lấy danh sách thành viên thành công",
        data=members_data_list,
        path=str(request.url.path)
    )