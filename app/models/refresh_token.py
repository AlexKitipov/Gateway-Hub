from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database.base import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    token_id_hash = Column(String(64), unique=True, nullable=False, index=True)
    family_id = Column(String(64), nullable=False, index=True)
    parent_token_id = Column(
        Integer, ForeignKey("refresh_tokens.id", ondelete="SET NULL"), nullable=True
    )
    replaced_by_token_id = Column(
        Integer, ForeignKey("refresh_tokens.id", ondelete="SET NULL"), nullable=True
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    revoked_at = Column(DateTime, nullable=True)
    reuse_detected_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="refresh_tokens")
    parent = relationship(
        "RefreshToken",
        remote_side=[id],
        foreign_keys=[parent_token_id],
        post_update=True,
    )
    replaced_by = relationship(
        "RefreshToken",
        remote_side=[id],
        foreign_keys=[replaced_by_token_id],
        post_update=True,
    )

    def __repr__(self):
        is_revoked = self.revoked_at is not None
        return (
            f"<RefreshToken(id={self.id}, user_id={self.user_id}, "
            f"revoked={is_revoked})>"
        )
