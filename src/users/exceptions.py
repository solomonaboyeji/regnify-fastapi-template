from src.exceptions import BaseConflictException, BaseNotFoundException


class UserNotFoundException(BaseNotFoundException):
    pass


class RoleNotFound(BaseNotFoundException):
    pass


class ProfileNotFoundException(BaseNotFoundException):
    pass


class DuplicateUserException(BaseConflictException):
    pass
