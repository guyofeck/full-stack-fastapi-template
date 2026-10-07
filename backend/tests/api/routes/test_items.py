import uuid

import pytest

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from tests.utils.item import create_random_item


def test_create_item(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"title": "Foo", "description": "Fighters"}
    response = client.post(
        f"{settings.API_V1_STR}/items/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert "id" in content
    assert "owner_id" in content


def test_read_item(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    item = create_random_item(db)
    response = client.get(
        f"{settings.API_V1_STR}/items/{item.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == item.title
    assert content["description"] == item.description
    assert content["id"] == str(item.id)
    assert content["owner_id"] == str(item.owner_id)


def test_read_item_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/items/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Item not found"


def test_read_item_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    item = create_random_item(db)
    response = client.get(
        f"{settings.API_V1_STR}/items/{item.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_read_items(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    create_random_item(db)
    create_random_item(db)
    response = client.get(
        f"{settings.API_V1_STR}/items/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["data"]) >= 2


@pytest.mark.parametrize("as_superuser", [True, False])
def test_search_items(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    normal_user_token_headers: dict[str, str],
    db: Session,
    as_superuser: bool,
) -> None:
    headers = superuser_token_headers if as_superuser else normal_user_token_headers
    marker = uuid.uuid4().hex
    created_ids = []
    for title, description in [
        (f"{marker} Alpha", "First"),
        (f"{marker} ALPHABET", "Second"),
        (f"{marker} Other", "Alpha only in description"),
        (f"{marker} 100%_done", "Literal wildcard characters"),
    ]:
        response = client.post(
            f"{settings.API_V1_STR}/items/",
            headers=headers,
            json={"title": title, "description": description},
        )
        assert response.status_code == 200
        created_ids.append(response.json()["id"])

    foreign_item = create_random_item(db)
    foreign_item.title = f"{marker} Alpha foreign"
    db.add(foreign_item)
    db.commit()

    response = client.get(
        f"{settings.API_V1_STR}/items/",
        headers=headers,
        params={"q": f"  {marker} aLpHa  ", "limit": 1},
    )
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == (3 if as_superuser else 2)
    assert len(content["data"]) == 1
    response = client.get(
        f"{settings.API_V1_STR}/items/",
        headers=headers,
        params={"q": f"{marker} alpha", "skip": 1, "limit": 1},
    )
    assert response.json()["count"] == content["count"]
    assert response.json()["data"][0]["id"] != content["data"][0]["id"]

    response = client.get(
        f"{settings.API_V1_STR}/items/",
        headers=headers,
        params={"q": f"{marker} 100%_"},
    )
    assert response.json()["count"] == 1
    assert response.json()["data"][0]["id"] == created_ids[3]

    response = client.get(
        f"{settings.API_V1_STR}/items/",
        headers=headers,
        params={"q": f"{marker} missing"},
    )
    assert response.json() == {"data": [], "count": 0}

    for q in ["", "   "]:
        response = client.get(
            f"{settings.API_V1_STR}/items/", headers=headers, params={"q": q}
        )
        unfiltered = client.get(f"{settings.API_V1_STR}/items/", headers=headers)
        assert response.json() == unfiltered.json()


def test_update_item(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    item = create_random_item(db)
    data = {"title": "Updated title", "description": "Updated description"}
    response = client.put(
        f"{settings.API_V1_STR}/items/{item.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert content["id"] == str(item.id)
    assert content["owner_id"] == str(item.owner_id)


def test_update_item_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"title": "Updated title", "description": "Updated description"}
    response = client.put(
        f"{settings.API_V1_STR}/items/{uuid.uuid4()}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Item not found"


def test_update_item_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    item = create_random_item(db)
    data = {"title": "Updated title", "description": "Updated description"}
    response = client.put(
        f"{settings.API_V1_STR}/items/{item.id}",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_delete_item(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    item = create_random_item(db)
    response = client.delete(
        f"{settings.API_V1_STR}/items/{item.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == "Item deleted successfully"


def test_delete_item_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.delete(
        f"{settings.API_V1_STR}/items/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Item not found"


def test_delete_item_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    item = create_random_item(db)
    response = client.delete(
        f"{settings.API_V1_STR}/items/{item.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Not enough permissions"
