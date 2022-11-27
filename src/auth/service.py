from typing import List

from src.users.models import User, UserScope


def retrieve_user_scopes(user: User) -> List[str]:
    scopes_to_return = ["me"]

    # * append the roles' permissions

    return scopes_to_return
