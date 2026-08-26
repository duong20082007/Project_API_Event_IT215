from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
import app.core.security as security

def register_user(db: Session, user_in: UserCreate):
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email đã được sử dụng"
        )
    
    new_user = User(
        email=user_in.email,
        password_hash=security.get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role="USER" 
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except Exception as e:
        db.rollback() 
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

def authenticate_user(db: Session, user_in: UserLogin):
    user = db.query(User).filter(User.email == user_in.email).first()
    
    if not user or not security.verify_password(user_in.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Email hoặc mật khẩu không chính xác."
        )
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Tài khoản của bạn đã bị khóa."
        )
    
    access_token = security.create_access_token(data={"sub": str(user.id)})
    refrest_token = security.create_refrest_token(data={'sub': str(user.id)})

    return {"access_token": access_token, "refrest_token": refrest_token, "token_type": "bearer"}