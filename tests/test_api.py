from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.config import settings
from backend.app.database import Base, get_db
from backend.app.main import app


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_sessions = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)
    monkeypatch.setattr(settings, "upload_dir", str(tmp_path / "uploads"))

    def override_get_db() -> Generator[Session, None, None]:
        db = testing_sessions()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def create_account(client: TestClient, email: str, name: str) -> tuple[dict, dict[str, str]]:
    response = client.post(
        "/users",
        json={"name": name, "email": email, "password": "local-test-password"},
    )
    assert response.status_code == 201, response.text
    account = response.json()
    headers = {"Authorization": f"Bearer {account['access_token']}"}
    return account, headers


def test_video_platform_workflow(client: TestClient) -> None:
    account, owner_headers = create_account(client, "creator@example.com", "Creadora")
    login = client.post(
        "/login",
        json={"email": "creator@example.com", "password": "local-test-password"},
    )
    assert login.status_code == 200
    assert client.get("/videos").json() == []

    created = client.post(
        "/videos",
        headers=owner_headers,
        data={"title": "Prueba local", "description": "Video de integración"},
        files={"video_file": ("sample.mp4", b"test-mp4-content", "video/mp4")},
    )
    assert created.status_code == 201, created.text
    video = created.json()
    assert video["user_name"] == "Creadora"
    assert client.get(f"/videos/{video['id']}").json()["views"] == 1

    comment = client.post(
        f"/videos/{video['id']}/comments",
        headers=owner_headers,
        json={"content": "Buen video"},
    )
    assert comment.status_code == 201, comment.text
    assert len(client.get(f"/videos/{video['id']}/comments").json()) == 1
    assert client.get(f"/users/{account['user']['id']}", headers=owner_headers).json()["video_count"] == 1

    _, other_headers = create_account(client, "other@example.com", "Otra persona")
    forbidden = client.put(
        f"/videos/{video['id']}",
        headers=other_headers,
        data={"title": "Cambio ajeno", "description": "No autorizado"},
    )
    assert forbidden.status_code == 403

    updated = client.put(
        f"/videos/{video['id']}",
        headers=owner_headers,
        data={"title": "Actualizado", "description": "Editado"},
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["title"] == "Actualizado"
    assert client.delete(f"/videos/{video['id']}", headers=owner_headers).status_code == 204
    assert client.get("/videos").json() == []
