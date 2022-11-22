"""Local Config"""

from src.service import get_settings


def get_default_avatar_url(first_name: str, last_name: str):
    app_settings = get_settings()

    ui_avatar_url = (
        f"https://ui-avatars.com/api/?name={last_name}+{first_name}&size=300"
    )

    if not app_settings.default_avatar_url:
        return ui_avatar_url

    return app_settings.default_avatar_url
