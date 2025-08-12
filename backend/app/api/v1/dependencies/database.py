from typing import Generator
from sqlalchemy.orm import Session

from app.database.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    データベースセッションを生成する依存関数
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()