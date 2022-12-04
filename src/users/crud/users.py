from uuid import UUID
from typing import Union
from sqlalchemy.orm import Session
from src.config import setup_logger
from src.exceptions import GeneralException
from src.security import get_password_hash
from src.users import models, schemas
from src.users.config import get_default_avatar_url
from src.users.exceptions import ProfileNotFoundException, UserNotFoundException

from sqlalchemy.exc import IntegrityError


class UserCRUD:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.logger = setup_logger()

    def get_user(self, user_id: UUID) -> Union[models.User, None]:
        return self.db.query(models.User).filter(models.User.id == user_id).first()  # type: ignore

    def get_user_by_email(self, email: str) -> models.User:
        return self.db.query(models.User).filter(models.User.email == email).first()  # type: ignore

    def get_users(self, skip: int = 0, limit: int = 100) -> list[models.User]:
        return self.db.query(models.User).offset(skip).limit(limit).all()

    def get_total_users(self) -> int:
        return self.db.query(models.User).count()

    def update_user_password(self, user_id: UUID, hashed_password: str) -> models.User:
        user: models.User = self.get_user(user_id)  # type: ignore
        if not user:
            raise UserNotFoundException(f"User with ID {user_id} does not exist")

        setattr(user, "hashed_password", hashed_password)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def update_user(self, user_id: UUID, data: schemas.UserUpdate):
        user: models.User = self.get_user(user_id)  # type: ignore
        if not user:
            return UserNotFoundException()

        data_without_none: dict = data.dict(exclude_none=True)

        for key in data_without_none:
            setattr(user.profile, key, data_without_none[key])

        for key in data_without_none:
            setattr(user, key, data_without_none[key])

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def create_user(
        self,
        user: schemas.UserCreate,
        should_make_active: bool = False,
        is_super_admin: bool = False,
    ):
        try:
            db_profile = self.create_user_profile(
                schemas.ProfileCreate(
                    **{
                        "last_name": user.last_name,
                        "first_name": user.first_name,
                        "avatar_url": get_default_avatar_url(
                            user.first_name, user.last_name
                        ),
                    }
                )
            )

            hashed_password = get_password_hash(user.password)
            db_user = models.User(
                email=user.email,
                hashed_password=hashed_password,
                profile=db_profile,
                is_active=should_make_active,
                is_super_admin=is_super_admin,
            )  # type: ignore
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            return db_user
        except IntegrityError as raised_exception:
            self.logger.exception(raised_exception)
            self.logger.error(raised_exception)
            raise GeneralException("A user with that email address already exist.")
        except Exception as raised_exception:
            self.logger.exception(raised_exception)
            self.logger.error(raised_exception)
            raise GeneralException(str(raised_exception))
        finally:
            self.db.rollback()

    def get_user_profile(self, user_id: str):
        db_profile = (
            self.db.query(models.Profile)
            .filter(models.Profile.user.id == user_id)
            .first()
        )
        if not db_profile:
            raise ProfileNotFoundException()

    def create_user_profile(self, profile: schemas.ProfileCreate) -> models.Profile:
        db_profile = models.Profile(**profile.dict())
        self.db.add(db_profile)
        self.db.commit()
        self.db.refresh(db_profile)
        return db_profile
