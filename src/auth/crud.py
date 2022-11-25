from sqlalchemy.orm import Session
from src.config import setup_logger


class AuthCRUD:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.logger = setup_logger()
