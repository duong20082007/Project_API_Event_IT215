from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
import jwt
import app.core.config as config
from app.db.database import get_db
from app.models.user import User

security_scheme = HTTPBearer()

def get_token_from_request(request: Request, auth_data = Depends(security_scheme)) -> str:
    if not auth_data or not auth_data.credentials:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Không tìm thấy token xác thực."
        )
    return auth_data.credentials

def get_current_user(token: str = Depends(get_token_from_request), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Token không chứa thông tin định danh."
            )
            
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token đã hết hạn. Vui lòng đăng nhập lại."
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Không thể xác minh Token."
        )
        
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Không tìm thấy người dùng sở hữu token này."
        )
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Tài khoản của bạn đã bị khóa."
        )
        
    return user

def get_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Quyền truy cập bị từ chối. Cần quyền ADMIN."
        )
    return current_user