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

def test_search_filter_composition():
    """
    Tests GET /catalog/search?q=&category=&language=&section= with composed AND filters.
    """
    # 1. Query search
    res = client.get("/catalog/search?q=Moti")
    assert res.status_code == 200
    data = res.json()
    assert data["total_results"] > 0

    # 2. Composed filter: q=Moti AND section=featured AND language=hi
    res_composed = client.get("/catalog/search?q=Moti&section=featured&language=hi")
    assert res_composed.status_code == 200
    comp_data = res_composed.json()
    for item in comp_data["results"]:
        assert item["section"] == "featured"
        assert "hi" in item["languages"]
        assert "moti" in item["show_title"].lower() or "moti" in item["episode_title"].lower()

    # 3. Non-matching filter combination returns 0 results cleanly
    res_empty = client.get("/catalog/search?q=Moti&section=songs")
    assert res_empty.status_code == 200
    assert res_empty.json()["total_results"] == 0
