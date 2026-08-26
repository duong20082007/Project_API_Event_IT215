from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.user import UserCreate, UserLogin
from app.schemas.response import APIResponse
import app.services.auth_service as auth_svc

router = APIRouter(prefix="/auth", tags=["Authentication"])

login_attempts = {}
MAX_ATTEMPTS = 5
LOCKOUT_MINUTES = 15

@router.post("/register", response_model=APIResponse)
def register(user_in: UserCreate, request: Request, db: Session = Depends(get_db)):
    user = auth_svc.register_user(db=db, user_in=user_in)
    
    user_data = {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at
    }
    
    return APIResponse(
        statusCode=status.HTTP_201_CREATED,
        message="Tạo tài khoản thành công",
        data=user_data,
        errors=None,
        path=str(request.url.path)
    )

@router.post("/login", response_model=APIResponse)
def login(user_in: UserLogin, request: Request, db: Session = Depends(get_db)):
    tokens = auth_svc.authenticate_user(db=db, user_in=user_in)
    
    return APIResponse(
        statusCode=status.HTTP_200_OK,
        message="Đăng nhập thành công",
        data=tokens,
        errors=None,
        path=str(request.url.path)
    )