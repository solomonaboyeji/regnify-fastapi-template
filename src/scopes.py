import enum


class ProfileScope(enum.Enum):
    CREATE = "profile:create"
    READ = "profile:read"
    UPDATE = "profile:update"
    DELETE = "profile:delete"


class UserScope(enum.Enum):
    CREATE = "user:create"
    READ = "user:read"
    UPDATE = "user:update"
    DELETE = "user:delete"


class RoleScope(enum.Enum):
    CREATE = "role:create"
    READ = "role:read"
    UPDATE = "role:update"
    DELETE = "role:delete"
