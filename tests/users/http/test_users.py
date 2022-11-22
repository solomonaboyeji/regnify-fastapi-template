from fastapi.testclient import TestClient

from src.main import app
from src.config import setup_logger

logger = setup_logger()

client = TestClient(app)


def test_only_super_admin_can_create_user(test_admin_user_headers: dict) -> None:
    logger.info(test_admin_user_headers)

    response = client.get("/")
    assert response.status_code == 200, response.json()
    assert "message" in response.json()
    assert response.json()["message"] == "Hello, Welcome to REGNIFY"
