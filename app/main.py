from fastapi import FastAPI
from app.db.database import engine, Base

import app.models.user
import app.models.event
import app.models.event_task
from app.core.exceptions import custom_http_exception_handler
from app.routers import auth, users
from app.routers import auth, users  
from app.routers import events

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Event Management API")

app.add_exception_handler(Exception, custom_http_exception_handler)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "System is running smoothly."}

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(events.router)