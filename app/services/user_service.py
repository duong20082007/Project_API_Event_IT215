from sqlalchemy.orm import Session
from typing import Optional
from app.models.user import User

def get_all_users(db: Session, search: Optional[str] = None, is_active: Optional[bool] = None):
    query = db.query(User)
    
    if search:
        query = query.filter(
            (User.full_name.ilike(f"%{search}%")) | 
            (User.email.ilike(f"%{search}%"))
        )
        
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
        
    return query.all()