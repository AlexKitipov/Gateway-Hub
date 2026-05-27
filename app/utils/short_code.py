import random

from sqlalchemy.orm import Session

from app.config import settings
from app.models.link import Link


async def generate_short_code(db: Session, length: int = None) -> str:
    """Generate a unique short code"""
    if length is None:
        length = settings.SHORT_CODE_LENGTH

    alphabet = settings.SHORT_CODE_ALPHABET
    max_attempts = 100

    for _ in range(max_attempts):
        code = "".join(random.choice(alphabet) for _ in range(length))

        existing = db.query(Link).filter(Link.code == code).first()
        if not existing:
            return code

    return await generate_short_code(db, length + 1)
