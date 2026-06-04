from app.database.base import Base
from app.database.session import engine


def init_db():
    """Initialize database by creating all tables."""
    from app import models  # noqa: F401 - ensure model metadata is registered

    Base.metadata.create_all(bind=engine)
