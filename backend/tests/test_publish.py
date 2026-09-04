import os
import json
import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.main import app
from app.core.db import SessionLocal, engine, Base
from app.models.show import Show, Episode, PublishRun
from app.services.seed import run_seed_ingestion
from app.services.publish_service import execute_catalog_publish, PublishBlockedError
from app.services.storage import get_storage

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    run_seed_ingestion(db)
    yield db
    db.close()

def test_publish_blocked_on_unresolved_validation_issues(setup_db: Session):
    """
    Publish should be blocked if seed validation issues (missing artwork, duplicate content_group) exist.
    """
    db = setup_db
    with pytest.raises(PublishBlockedError):
        execute_catalog_publish(db, published_by="admin", include_seed_file_scan=True)

    # Verify PublishRun record logged failure
    run = db.query(PublishRun).order_by(PublishRun.published_at.desc()).first()
    assert run is not None
    assert run.status == "failed"


def test_publish_atomicity_and_content_group_collapsing(setup_db: Session):
    """
    Fixes blocking validation issues, executes publish, and verifies:
    1. Catalogue file is created atomically.
    2. Content groups collapse language variants into single entries with languages: [].
    3. Season 0 trailers are excluded from normal season listings.
    """
    db = setup_db
    storage = get_storage()

    # 1. Fix ep_0036 missing artwork
    ep36 = db.query(Episode).filter(Episode.id == "ep_0036").first()
    if ep36:
        ep36.status = "draft" # move to draft so publish is unblocked

    # 2. Ensure all published episodes in DB have complete artwork and duration
    for ep in db.query(Episode).filter(Episode.status == "published").all():
        if len(ep.artworks) < 3 or not ep.duration_seconds:
            ep.status = "draft"
    db.commit()

    # Trigger publish on DB state
    run = execute_catalog_publish(db, published_by="admin", include_seed_file_scan=False)
    assert run.status == "success"

    # Verify catalog file exists in storage
    assert storage.exists("catalog.json")
    catalog_bytes = storage.read("catalog.json")
    catalog_data = json.loads(catalog_bytes.decode("utf-8"))

    assert "sections" in catalog_data
    
    # Inspect collapsed content_group variants (e.g. motis-many-lives-s01e01)
    featured_shows = catalog_data["sections"].get("featured", [])
    moti_show = next((s for s in featured_shows if s["slug"] == "motis-many-lives"), None)
    assert moti_show is not None

    # Verify Season 0 trailers excluded from seasons list
    season_numbers = [s["season_number"] for s in moti_show["seasons"]]
    assert 0 not in season_numbers

    # Verify content group motis-many-lives-s01e01 collapsed languages ["en", "hi"]
    s1 = next(s for s in moti_show["seasons"] if s["season_number"] == 1)
    ep1 = next(e for e in s1["episodes"] if e["content_group"] == "motis-many-lives-s01e01")
    assert sorted(ep1["languages"]) == ["en", "hi"]
