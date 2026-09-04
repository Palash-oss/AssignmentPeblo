import os
import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi.testclient import TestClient

from app.main import app
from app.core.db import SessionLocal, engine, Base
from app.models.show import Show, Season, Episode
from app.services.seed import run_seed_ingestion
from app.services.validation_service import generate_validation_report

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    run_seed_ingestion(db)
    yield db
    db.close()

def test_uniqueness_ep0004_and_ep9001_collision(setup_db: Session):
    """
    Confirms episode ep_0004 and ep_9001 collision on (content_group="motis-many-lives-s01e02", language="hi")
    violates unique constraint and is flagged in the validation report.
    """
    db = setup_db
    
    # 1. ep_0004 exists in seeded DB
    ep0004 = db.query(Episode).filter(Episode.id == "ep_0004").first()
    assert ep0004 is not None
    assert ep0004.content_group == "motis-many-lives-s01e02"
    assert ep0004.language == "hi"

    # 2. Attempting to manually insert ep_9001 with same content_group and language raises IntegrityError
    show = db.query(Show).first()
    season = db.query(Season).filter(Season.show_id == show.id).first()
    
    ep9001 = Episode(
        id="ep_9001",
        show_id=show.id,
        season_id=season.id,
        episode_number=2,
        episode_title="Rain on the Roof Duplicate",
        language="hi",
        content_group="motis-many-lives-s01e02",
        status="published"
    )
    db.add(ep9001)
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()

    # 3. Validation report surfaces duplicate content_group/language collision
    report = generate_validation_report(db)
    assert not report["is_publishable"]
    duplicates = report["issues_by_category"]["duplicate_content_group_language"]
    assert len(duplicates) >= 1
    
    target_dup = next(d for d in duplicates if d["content_group"] == "motis-many-lives-s01e02" and d["language"] == "hi")
    assert "ep_0004" in target_dup["episode_ids"]
    assert "ep_9001" in target_dup["episode_ids"]
