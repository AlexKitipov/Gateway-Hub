from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database.base import Base


class Link(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    code = Column(String(20), unique=True, nullable=False, index=True)
    target_url = Column(Text, nullable=False)
    title = Column(String(255))
    description = Column(Text)
    click_count = Column(BigInteger, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    expires_at = Column(DateTime, nullable=True, index=True)
    custom_domain = Column(String(255), nullable=True)

    # Relationships
    user = relationship("User", back_populates="links")
    analytics = relationship(
        "LinkAnalytics", back_populates="link", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Link(code={self.code}, target_url={self.target_url})>"
