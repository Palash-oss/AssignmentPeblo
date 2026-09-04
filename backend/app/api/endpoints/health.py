from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.db import get_db
from app.services.storage import get_storage

router = APIRouter(tags=["health"])

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    db_status = "unhealthy"
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"disconnected: {str(e)}"

    storage_status = "unhealthy"
    try:
        storage = get_storage()
        test_key = "health_check.tmp"
        storage.save(test_key, "health_ok")
        if storage.exists(test_key):
            storage.delete(test_key)
            storage_status = "writable"
    except Exception as e:
        storage_status = f"unwritable: {str(e)}"

    is_healthy = db_status == "connected" and storage_status == "writable"
    status_code = 200 if is_healthy else 500

    return Response(
        content=f'{{"status": "{"healthy" if is_healthy else "unhealthy"}", "database": "{db_status}", "storage": "{storage_status}"}}',
        media_type="application/json",
        status_code=status_code
    )
