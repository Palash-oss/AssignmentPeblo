import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.db import engine, Base, SessionLocal
from app.api.endpoints import admin, catalog, health
from app.services.seed import run_seed_ingestion

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Peblo TV Full-Stack API for CMS Editorial & Netflix-style Viewer UI",
    version="1.0.0"
)

# CORS middleware for CMS & Viewer UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file mount for local disk storage
storage_dir = os.path.abspath(settings.STORAGE_DIR)
os.makedirs(storage_dir, exist_ok=True)
app.mount("/storage", StaticFiles(directory=storage_dir), name="storage")

# Include Routers
app.include_router(health.router)
app.include_router(catalog.router)
app.include_router(admin.router)

@app.on_event("startup")
def startup_event():
    # Ingest seed data if available
    db = SessionLocal()
    try:
        run_seed_ingestion(db)
    finally:
        db.close()
