import uuid

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


def test_read_items_title_filter(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    marker = str(uuid.uuid4())
    first = create_random_item(db)
    second = create_random_item(db)
    description_only = create_random_item(db)
    first.title = f"First {marker} TITLE"
    second.title = f"Second {marker} title"
    description_only.description = marker
    db.add_all([first, second, description_only])
    db.commit()

    response = client.get(
        f"{settings.API_V1_STR}/items/",
        headers=superuser_token_headers,
        params={"title": f"{marker} tItLe", "limit": 1},
    )
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 2
    assert len(content["data"]) == 1
    assert content["data"][0]["id"] in {str(first.id), str(second.id)}

    response = client.get(
        f"{settings.API_V1_STR}/items/",
        headers=superuser_token_headers,
        params={"title": str(uuid.uuid4())},
    )
    assert response.json() == {"data": [], "count": 0}


def test_read_items_title_filter_preserves_ownership(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    superuser_token_headers: dict[str, str],
    db: Session,
) -> None:
    title = f"Search {uuid.uuid4()}"
    own_item = client.post(
        f"{settings.API_V1_STR}/items/",
        headers=normal_user_token_headers,
        json={"title": title},
    ).json()
    other_item = create_random_item(db)
    other_item.title = title
    db.add(other_item)
    db.commit()

    response = client.get(
        f"{settings.API_V1_STR}/items/",
        headers=normal_user_token_headers,
        params={"title": title},
    )
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 1
    assert [item["id"] for item in content["data"]] == [own_item["id"]]

    response = client.get(
        f"{settings.API_V1_STR}/items/",
        headers=superuser_token_headers,
        params={"title": title},
    )
    assert response.json()["count"] == 2


def test_read_items_title_filter_literal_wildcards(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    marker = str(uuid.uuid4())
    match = create_random_item(db)
    other = create_random_item(db)
    match.title = f"{marker}%_literal"
    other.title = f"{marker}XXliteral"
    db.add_all([match, other])
    db.commit()

    response = client.get(
        f"{settings.API_V1_STR}/items/",
        headers=superuser_token_headers,
        params={"title": f"{marker}%_"},
    )
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 1
    assert content["data"][0]["id"] == str(match.id)


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
