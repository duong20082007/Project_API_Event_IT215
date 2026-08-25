from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db
from app.schemas.response import APIResponse
from app.models.user import User
from app.dependencies.auth_deps import get_current_user, get_admin_user

import app.services.user_service as user_svc

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=APIResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    profile_data = {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at
    }
    
    return APIResponse(
        statusCode=200,
        message="Lấy thông tin hồ sơ thành công.",
        data=profile_data
    )

@router.get("", response_model=APIResponse)
def get_users(
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_admin_user) 
):
    users = user_svc.get_all_users(db=db, search=search, is_active=is_active)
    
    users_data_list = [
        {
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role,
            "is_active": u.is_active,
            "created_at": u.created_at
        }
        for u in users
    ]
    
    return APIResponse(
        statusCode=200,
        message="Lấy danh sách người dùng thành công.",
        data=users_data_list
    )