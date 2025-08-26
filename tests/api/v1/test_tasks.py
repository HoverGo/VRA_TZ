# test_task_manager.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from src.main import app
from src.core.dependencies.db_dependency import DBManager


# Создаем тестовый менеджер БД
test_db_manager = DBManager('test_tasks.db')

# Мокаем зависимость БД для тестов
@pytest.fixture(autouse=True)
def mock_db_dependency():
    with patch('src.api.v1.tasks.db_manager', test_db_manager):
        yield


@pytest.fixture(autouse=True)
def clean_db():
    # Чистим тестовую БД перед каждым тестом
    with test_db_manager.get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks")
        conn.commit()


client = TestClient(app)


BASE = "/api/v1"


def test_create_task():
    response = client.post(
        f"{BASE}/tasks",
        params={
            "title": "Test Task",
            "description": "Test Description",
            "status": "created",
        },
    )

    data = response.json()
    assert response.status_code == 201
    assert data["title"] == "Test Task"
    assert data["description"] == "Test Description"
    assert data["status"] == "created"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_get_task():
    create_response = client.post(
        f"{BASE}/tasks",
        params={
            "title": "Get Test Task",
            "description": "Test getting",
            "status": "created",
        },
    )
    task_id = create_response.json()["id"]

    response = client.get(f"{BASE}/tasks/{task_id}", params={"id": task_id})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Get Test Task"


def test_get_nonexistent_task():
    response = client.get(f"{BASE}/tasks/nonexistent-id", params={"id": "nonexistent-id"})
    assert response.status_code == 404


def test_get_tasks():
    client.post(f"{BASE}/tasks", params={"title": "Task 1", "status": "created"})
    client.post(f"{BASE}/tasks", params={"title": "Task 2", "status": "in_progress"})

    response = client.get(f"{BASE}/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    titles = {item["title"] for item in data}
    assert {"Task 1", "Task 2"}.issubset(titles)


def test_get_tasks_filtered():
    client.post(f"{BASE}/tasks", params={"title": "Created Task", "status": "created"})
    client.post(f"{BASE}/tasks", params={"title": "In Progress Task", "status": "in_progress"})
    client.post(f"{BASE}/tasks", params={"title": "Completed Task", "status": "completed"})

    response = client.get(f"{BASE}/tasks?status=created")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["status"] == "created"


def test_update_task():
    create_response = client.post(
        f"{BASE}/tasks",
        params={
            "title": "Original Title",
            "description": "Original Description",
            "status": "created",
        },
    )
    task_id = create_response.json()["id"]

    update_response = client.patch(
        f"{BASE}/tasks/{task_id}",
        params={
            "id": task_id,
            "title": "Updated Title",
            "status": "in_progress",
        },
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["title"] == "Updated Title"
    assert data["status"] == "in_progress"
    assert data["description"] == "Original Description"


def test_update_nonexistent_task():
    response = client.patch(
        f"{BASE}/tasks/nonexistent-id",
        params={
            "id": "nonexistent-id",
            "title": "New Title",
        },
    )
    assert response.status_code == 404


def test_update_without_fields_returns_400():
    create_response = client.post(f"{BASE}/tasks", params={"title": "Some Title", "status": "created"})
    task_id = create_response.json()["id"]

    response = client.patch(f"{BASE}/tasks/{task_id}", params={"id": task_id})
    assert response.status_code == 400


def test_delete_task():
    create_response = client.post(f"{BASE}/tasks", params={"title": "Task to delete", "status": "created"})
    task_id = create_response.json()["id"]

    delete_response = client.delete(f"{BASE}/tasks/{task_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"{BASE}/tasks/{task_id}", params={"id": task_id})
    assert get_response.status_code == 404


def test_delete_nonexistent_task():
    response = client.delete(f"{BASE}/tasks/nonexistent-id")
    assert response.status_code == 404


def test_validation():
    response = client.post(f"{BASE}/tasks", params={"title": "", "status": "created"})
    assert response.status_code == 422

    response = client.post(f"{BASE}/tasks", params={"title": "Test", "status": "invalid"})
    assert response.status_code == 422