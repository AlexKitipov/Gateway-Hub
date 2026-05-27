from app import models
from app.database.base import Base
from app.database.session import engine


def init_db():
    """Initialize database by creating all tables"""
    Base.metadata.create_all(bind=engine)
