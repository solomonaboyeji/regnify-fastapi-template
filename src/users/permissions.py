"""Allows the user to read all the users in the system"""
CAN_READ_ALL_USERS = "CAN_READ_ALL_USERS"
CAN_CREATE_SPECIAL_USER = "CAN_CREATE_SPECIAL_USER"


def get_regular_user_permissions() -> list[str]:
    return []
