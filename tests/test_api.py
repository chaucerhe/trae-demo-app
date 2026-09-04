"""待办 API 测试：pytest + FastAPI TestClient"""
import pytest
from fastapi.testclient import TestClient

from app import main as app_module
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_todos():
    app_module._todos.clear()
    yield
    app_module._todos.clear()


def test_create_todo():
    r = client.post("/todos", json={"title": "买牛奶"})
    assert r.status_code == 201
    body = r.json()
    assert body["title"] == "买牛奶"
    assert body["done"] is False
    assert body["id"]


def test_list_todos():
    client.post("/todos", json={"title": "A"})
    client.post("/todos", json={"title": "B"})
    r = client.get("/todos")
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_sort_created_at_desc():
    client.post("/todos", json={"title": "first"})
    client.post("/todos", json={"title": "second"})
    r = client.get("/todos", params={"sort": "created_at:desc"})
    assert r.status_code == 200
    titles = [t["title"] for t in r.json()]
    assert titles[0] == "second"


def test_update_todo():
    tid = client.post("/todos", json={"title": "旧标题"}).json()["id"]
    r = client.patch(f"/todos/{tid}", json={"title": "新标题", "done": True})
    assert r.status_code == 200
    assert r.json()["title"] == "新标题"
    assert r.json()["done"] is True


def test_delete_todo():
    tid = client.post("/todos", json={"title": "删除我"}).json()["id"]
    r = client.delete(f"/todos/{tid}")
    assert r.status_code == 204
    assert client.get("/todos").json() == []


def test_update_missing_returns_404():
    r = client.patch("/todos/not-exist", json={"title": "x"})
    assert r.status_code == 404


def test_healthz():
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_list_todos_default_order():
    client.post("/todos", json={"title": "A"})
    client.post("/todos", json={"title": "B"})
    client.post("/todos", json={"title": "C"})
    r = client.get("/todos")
    assert r.status_code == 200
    titles = [t["title"] for t in r.json()]
    assert titles == ["A", "B", "C"]


def test_sort_unknown_value_ignored():
    client.post("/todos", json={"title": "first"})
    client.post("/todos", json={"title": "second"})
    r = client.get("/todos", params={"sort": "unknown_value"})
    assert r.status_code == 200
    titles = [t["title"] for t in r.json()]
    assert titles == ["first", "second"]
