from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.base import Base


class LinkAnalytics(Base):
    __tablename__ = "link_analytics"

    id = Column(Integer, primary_key=True, index=True)
    link_id = Column(
        Integer, ForeignKey("links.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_agent = Column(Text)
    referer = Column(Text)
    ip_address = Column(String(45), index=True)
    country = Column(String(2))
    city = Column(String(100))
    clicked_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    link = relationship("Link", back_populates="analytics")

    __table_args__ = (Index("idx_analytics_link_clicked", "link_id", "clicked_at"),)
