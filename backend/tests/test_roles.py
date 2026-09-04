import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.db import SessionLocal, engine, Base
from app.services.seed import run_seed_ingestion

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    run_seed_ingestion(db)
    yield db
    db.close()

def test_editor_can_access_admin_shows_and_validation():
    # Editor role allowed for CRUD and validation report
    res = client.get("/admin/shows", headers={"X-User-Role": "editor"})
    assert res.status_code == 200

    res = client.get("/admin/validation-report", headers={"X-User-Role": "editor"})
    assert res.status_code == 200

def test_editor_cannot_trigger_publish():
    # Editor role forbidden (403) from /admin/catalog/publish
    res = client.post("/admin/catalog/publish", headers={"X-User-Role": "editor"})
    assert res.status_code == 403
    assert "Permission denied" in res.json()["detail"]

def test_admin_can_trigger_publish():
    # Admin role permitted for publish route (returns 400 publish blocked due to seed issues, but passes 403 auth check)
    res = client.post("/admin/catalog/publish", headers={"X-User-Role": "admin"})
    assert res.status_code in (200, 400) # Auth passed
    assert res.status_code != 403
