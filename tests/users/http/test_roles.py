from fastapi.testclient import TestClient


from src.config import setup_logger
from src.scopes import RoleScope, UserScope
from src.users.models import User
from tests.users.http.conftest import login_test

logger = setup_logger()

CUSTOM_ROLE_TITLE = "Custom Role"

TEST_CACHE = {}


def test_create_role(
    client: TestClient, test_admin_user_headers: dict, test_non_admin_user_headers: dict
):
    # * super admin can create
    response = client.post(
        "/roles",
        headers=test_admin_user_headers,
        json={
            "title": "Role Roles",
            "permissions": [
                RoleScope.CREATE.value,
                RoleScope.READ.value,
                RoleScope.UPDATE.value,
                RoleScope.DELETE.value,
            ],
        },
    )
    assert response.status_code == 200, response.content
    assert response.json()["title"] == "Role Roles".lower()
    TEST_CACHE["ROLE_WRITE_SCOPE_ROLE"] = response.json()

    # * user without the right scope can not create
    role_title = CUSTOM_ROLE_TITLE + " 1"
    response = client.post(
        "/roles",
        headers=test_non_admin_user_headers,
        json={
            "title": role_title,
            "permissions": [RoleScope.CREATE.value],
        },
    )
    assert response.status_code == 403, response.content


def test_user_with_role_scope_can_create_role(
    client: TestClient,
    test_admin_user_headers: dict,
    test_non_admin_user: dict,
    test_password: str,
):

    # * assign the role to a user
    endpoint = f"/roles/{TEST_CACHE['ROLE_WRITE_SCOPE_ROLE']['id']}/assign-role?user_id={str(test_non_admin_user['id'])}"
    response = client.post(
        endpoint,
        headers=test_admin_user_headers,
        json={"user_id": str(test_non_admin_user["id"])},
    )
    assert response.status_code == 200, response.json()
    token = login_test(client, test_non_admin_user["email"], test_password)

    # * the user can now create a role

    response = client.post(
        "/roles",
        headers=token,
        json={
            "title": "User Roles",
            "permissions": [
                UserScope.CREATE.value,
                UserScope.READ.value,
                UserScope.UPDATE.value,
                UserScope.DELETE.value,
            ],
        },
    )
    assert response.status_code == 200, response.content
    assert response.json()["title"] == "User Roles".lower()
    TEST_CACHE["USER_WRITE_SCOPE_ROLE"] = response.json()


def test_get_roles(
    client: TestClient, test_admin_user_headers: dict, test_non_admin_user_headers: dict
):
    response = client.get("/roles", headers=test_admin_user_headers)
    assert response.status_code == 200, response.json()
    assert response.json()["total"] > 0
    assert len(response.json()["roles"]) > 0
    user_role_exist = False
    for role in response.json()["roles"]:
        if role["title"] == "User Roles".lower():
            user_role_exist = True

    assert user_role_exist

    response = client.get("/roles", headers=test_non_admin_user_headers)
    assert response.status_code == 200, response.json()
    assert response.json()["total"] > 0
    assert len(response.json()["roles"]) > 0


def test_get_roles_pagination(client: TestClient, test_non_admin_user_headers: dict):
    response = client.get("/roles?limit=1&start=1", headers=test_non_admin_user_headers)
    assert response.status_code == 200, response.json()
    assert response.json()["total"] > 0
    assert len(response.json()["roles"]) == 1


def test_get_role(
    client: TestClient, test_admin_user_headers: dict, test_non_admin_user_headers: dict
):
    response = client.get("/roles", headers=test_admin_user_headers)
    assert response.status_code == 200, response.json()
    assert response.json()["total"] > 0

    role_id = response.json()["roles"][0]["id"]

    response = client.get(f"roles/{role_id}", headers=test_non_admin_user_headers)
    assert response.status_code == 200, response.json()
    assert response.json()["id"] == role_id


def test_edit_role(
    client: TestClient,
    test_admin_user_headers: dict,
    test_non_admin_user_headers: dict,
    test_non_admin_user: dict,
    test_user_without_any_roles_user_headers: dict,
):
    response = client.get("/roles", headers=test_admin_user_headers)
    assert response.status_code == 200, response.json()
    assert response.json()["total"] > 0

    role_id = response.json()["roles"][0]["id"]
    role_title = response.json()["roles"][0]["title"]
    role_permissions: list = response.json()["roles"][0]["permissions"]

    role_permissions.append(UserScope.CREATE.value)

    response = client.put(
        f"/roles/{role_id}",
        headers=test_non_admin_user_headers,
        json={"title": role_title + " edited", "permissions": role_permissions},
    )
    assert response.status_code == 200, response.json()

    assert response.json()["title"] == role_title + " edited"
    assert response.json()["permissions"] == role_permissions
    assert response.json()["modified_by_user"]["id"] == str(test_non_admin_user["id"])

    # * test user with out role can not do this
    response = client.put(
        f"/roles/{role_id}",
        headers=test_user_without_any_roles_user_headers,
        json={"title": role_title + " edited", "permissions": role_permissions},
    )
    assert response.status_code == 403, response.json()


def test_get_role_by_title(client: TestClient, test_non_admin_user_headers: dict):
    response = client.get("/roles?limit=1&start=1", headers=test_non_admin_user_headers)
    assert response.status_code == 200, response.json()
    assert response.json()["total"] > 0
    assert len(response.json()["roles"]) == 1

    response = client.get(
        f"/roles?title={response.json()['roles'][0]['title']}",
        headers=test_non_admin_user_headers,
    )
    assert response.status_code == 200, response.json()
    assert response.json()["total"] == 1
    assert len(response.json()["roles"]) == 1


def test_role_ordering(client: TestClient, test_non_admin_user_headers: dict):

    # * test desc
    response = client.get(
        "/roles?order_by=DATE_CREATED&order_direction=DESC",
        headers=test_non_admin_user_headers,
    )
    assert response.status_code == 200, response.json()
    assert response.json()["total"] > 0

    previous_value = None
    for role in response.json()["roles"]:
        if previous_value is None:
            previous_value = role["date_created"]

        assert previous_value >= role["date_created"]

    # * test asc
    response = client.get(
        "/roles?order_by=DATE_CREATED&order_direction=ASC",
        headers=test_non_admin_user_headers,
    )
    assert response.status_code == 200, response.json()
    assert response.json()["total"] > 0

    previous_value = None
    for role in response.json()["roles"]:
        if previous_value is None:
            previous_value = role["date_created"]

        assert previous_value <= role["date_created"]


def test_get_users_assigned_to_a_role(
    client: TestClient, test_non_admin_user_headers: dict
):
    endpoint = f"/roles/{TEST_CACHE['ROLE_WRITE_SCOPE_ROLE']['id']}/list-assigned-users"
    response = client.get(endpoint, headers=test_non_admin_user_headers)
    assert response.status_code == 200, response.json()
    assert response.json()["total"] == 1
    assert len(response.json()["user_roles"]) == 1


def test_unassign_role(
    client: TestClient,
    test_admin_user_headers: dict,
    test_non_admin_user: dict,
    test_password: str,
):
    # * unassign the role to a user
    endpoint = f"/roles/{TEST_CACHE['ROLE_WRITE_SCOPE_ROLE']['id']}/unassign-role?user_id={str(test_non_admin_user['id'])}"
    response = client.post(
        endpoint,
        headers=test_admin_user_headers,
        json={"user_id": str(test_non_admin_user["id"])},
    )
    assert response.status_code == 200, response.json()
    token = login_test(client, test_non_admin_user["email"], test_password)

    # * the user can now create a role

    response = client.post(
        "/roles",
        headers=token,
        json={
            "title": "User Roles 2",
            "permissions": [UserScope.CREATE.value],
        },
    )
    assert response.status_code == 403, response.content


def test_delete_role(
    client: TestClient,
    test_admin_user_headers: dict,
    test_user_without_any_roles_user: User,
    test_password: str,
):

    # * create a role
    response = client.post(
        "/roles",
        headers=test_admin_user_headers,
        json={
            "title": "Test Role 1",
            "permissions": [RoleScope.CREATE.value],
        },
    )
    assert response.status_code == 200, response.content
    role_id = response.json()["id"]

    # * assign the role to a user
    endpoint = f"/roles/{role_id}/assign-role?user_id={str(test_user_without_any_roles_user['id'])}"
    response = client.post(
        endpoint,
        headers=test_admin_user_headers,
        json={"user_id": str(test_user_without_any_roles_user["id"])},
    )
    assert response.status_code == 200, response.json()
    token = login_test(client, test_user_without_any_roles_user["email"], test_password)

    # * delete the role
    response = client.delete(f"/roles/{role_id}", headers=test_admin_user_headers)
    assert response.status_code == 200, response.json()
    assert response.json()["detail"] == "1", response.content

    # * the user would not be able to create
    response = client.post(
        "/roles",
        headers=token,
        json={
            "title": "User Roles",
            "permissions": [UserScope.CREATE.value],
        },
    )
    assert response.status_code == 403, response.content
