from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime

def custom_http_exception_handler(request: Request, exc: HTTPException):
    current_path = request.url.path
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "statusCode": exc.status_code,
            "message": "Thất bại", 
            "data": None,
            "errors": exc.detail, 
            "timestamp": datetime.now(),
            "path": current_path
        }
    )