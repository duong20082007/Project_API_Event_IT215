from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import app.core.config as config

engine = create_engine(config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()