from curses import use_default_colors
from fastapi.testclient import TestClient

from src.main import app
from src.config import Settings, setup_logger

logger = setup_logger()

email_under_test = "1@regnify.com"
prefix = "http-user"


def test_only_super_admin_can_create_user(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200, response.json()
    assert "message" in response.json()
    assert response.json()["message"] == "Hello, Welcome to REGNIFY"


def test_can_create_user_with_admin_signup_token(
    client: TestClient, test_admin_user_headers: dict, app_settings: Settings
) -> None:
    user_data = {
        "email": email_under_test,
        "password": "simplePass123",
        "last_name": "",
        "first_name": "",
    }

    response = client.post(
        "/users",
        json=user_data,
        headers={
            **test_admin_user_headers,
            "admin-signup-token": app_settings.admin_signup_token,
        },
    )
    assert response.status_code == 200, response.json()
    assert response.json()["is_active"] == True
    assert response.json()["is_super_admin"] == False

    user_data = {
        **user_data,
        "email": prefix + email_under_test,
        "is_super_admin": True,
    }
    response = client.post(
        "/users",
        json=user_data,
        headers={
            **test_admin_user_headers,
            "admin-signup-token": app_settings.admin_signup_token,
        },
    )
    assert response.status_code == 200, response.json()
    assert response.json()["is_active"] == True
    assert response.json()["is_super_admin"] == True

    # * when admin signup token is invalid
    user_data = {**user_data, "email": "1" + prefix + email_under_test}
    response = client.post(
        "/users",
        json=user_data,
        headers={
            **test_admin_user_headers,
            "admin-signup-token": "THIS IS WRONG!",
        },
    )
    assert response.status_code == 200, response.json()
    assert response.json()["is_active"] == False
    assert response.json()["is_super_admin"] == False
