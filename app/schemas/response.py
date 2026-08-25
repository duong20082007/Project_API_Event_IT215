from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field

class APIResponse(BaseModel):
    statusCode: int = 200
    message: str = "Thành công"
    data: Optional[Any] = None
    errors: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    path: Optional[str] = None