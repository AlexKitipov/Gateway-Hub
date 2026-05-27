from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.database.base import Base


class LinkAnalytics(Base):
    __tablename__ = "link_analytics"

    id = Column(Integer, primary_key=True, index=True)
    link_id = Column(Integer, ForeignKey("links.id"), nullable=False, index=True)
    user_agent = Column(Text, nullable=True)
    referer = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    country = Column(String(2), nullable=True)
    clicked_at = Column(DateTime, server_default=func.now(), nullable=False)

    link = relationship("Link", back_populates="analytics")
