import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.core.db import get_db
from app.api.deps import require_editor, require_admin
from app.models.show import Show, Season, Episode, Artwork, PublishRun
from app.schemas.show import ShowBase, ShowCreate, ShowUpdate, EpisodeBase, EpisodeCreate, EpisodeUpdate, ArtworkBase
from app.services.validator import validate_artwork, ArtworkValidationError
from app.services.storage import get_storage
from app.services.validation_service import generate_validation_report, get_allowed_sections
from app.services.publish_service import execute_catalog_publish, PublishBlockedError

router = APIRouter(prefix="/admin", tags=["admin"])

# --- SHOWS CRUD ---

@router.get("/shows", response_model=List[ShowBase])
def list_shows(
    section: Optional[str] = None,
    db: Session = Depends(get_db),
    role: str = Depends(require_editor)
):
    query = db.query(Show)
    if section:
        query = query.filter(Show.section == section)
    return query.order_by(Show.title.asc()).all()

@router.post("/shows", response_model=ShowBase, status_code=201)
def create_show(
    payload: ShowCreate,
    db: Session = Depends(get_db),
    role: str = Depends(require_editor)
):
    allowed_sections = get_allowed_sections()
    if payload.section and payload.section not in allowed_sections:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid section '{payload.section}'. Allowed sections are: {', '.join(allowed_sections)}."
        )

    existing = db.query(Show).filter((Show.title == payload.title) | (Show.slug == payload.slug)).first()
    if existing:
        raise HTTPException(status_code=400, detail="A show with this title or slug already exists.")

    show = Show(
        title=payload.title,
        slug=payload.slug,
        section=payload.section,
        categories=payload.categories,
        synopsis=payload.synopsis
    )
    db.add(show)
    db.commit()
    db.refresh(show)
    return show

@router.get("/shows/{show_id}", response_model=ShowBase)
def get_show(
    show_id: str,
    db: Session = Depends(get_db),
    role: str = Depends(require_editor)
):
    show = db.query(Show).filter(Show.id == show_id).first()
    if not show:
        raise HTTPException(status_code=404, detail="Show not found")
    return show

@router.put("/shows/{show_id}", response_model=ShowBase)
def update_show(
    show_id: str,
    payload: ShowUpdate,
    db: Session = Depends(get_db),
    role: str = Depends(require_editor)
):
    show = db.query(Show).filter(Show.id == show_id).first()
    if not show:
        raise HTTPException(status_code=404, detail="Show not found")

    if payload.section:
        allowed_sections = get_allowed_sections()
        if payload.section not in allowed_sections:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid section '{payload.section}'. Allowed sections are: {', '.join(allowed_sections)}."
            )
        show.section = payload.section

    if payload.title:
        show.title = payload.title
    if payload.slug:
        show.slug = payload.slug
    if payload.categories is not None:
        show.categories = payload.categories
    if payload.synopsis is not None:
        show.synopsis = payload.synopsis

    db.commit()
    db.refresh(show)
    return show

# --- EPISODES CRUD ---

@router.get("/episodes")
def list_episodes(
    show_id: Optional[str] = None,
    section: Optional[str] = None,
    status: Optional[str] = None,
    language: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
    role: str = Depends(require_editor)
):
    query = db.query(Episode).join(Show)
    if show_id:
        query = query.filter(Episode.show_id == show_id)
    if section:
        query = query.filter(Show.section == section)
    if status:
        query = query.filter(Episode.status == status)
    if language:
        query = query.filter(Episode.language == language)
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            (Episode.episode_title.ilike(pattern)) |
            (Show.title.ilike(pattern)) |
            (Episode.content_group.ilike(pattern))
        )

    total = query.count()
    items = query.order_by(Episode.id.asc()).offset((page - 1) * limit).limit(limit).all()

    result_items = []
    for ep in items:
        ep_dict = {
            "id": ep.id,
            "show_id": ep.show_id,
            "show_title": ep.show.title if ep.show else "Unknown",
            "section": ep.show.section if ep.show else None,
            "season_number": ep.season.season_number if ep.season else 1,
            "episode_number": ep.episode_number,
            "episode_title": ep.episode_title,
            "duration_seconds": ep.duration_seconds,
            "language": ep.language,
            "content_group": ep.content_group,
            "status": ep.status,
            "artworks": [
                {
                    "id": a.id,
                    "artwork_type": a.artwork_type,
                    "url": a.url,
                    "width": a.width,
                    "height": a.height,
                    "file_size_kb": a.file_size_kb
                }
                for a in ep.artworks
            ]
        }
        result_items.append(ep_dict)

    return {
        "items": result_items,
        "total": total,
        "page": page,
        "limit": limit
    }

@router.post("/episodes", response_model=EpisodeBase, status_code=201)
def create_episode(
    payload: EpisodeCreate,
    db: Session = Depends(get_db),
    role: str = Depends(require_editor)
):
    # Verify show exists
    show = db.query(Show).filter(Show.id == payload.show_id).first()
    if not show:
        raise HTTPException(status_code=404, detail="Show not found")

    # Uniqueness check on (content_group, language)
    dup = db.query(Episode).filter(
        Episode.content_group == payload.content_group,
        Episode.language == payload.language
    ).first()
    if dup:
        raise HTTPException(
            status_code=400,
            detail=f"Conflict: Episode '{dup.id}' already exists with content_group '{payload.content_group}' and language '{payload.language}'."
        )

    # Get or create Season
    season = db.query(Season).filter(
        Season.show_id == show.id,
        Season.season_number == payload.season_number
    ).first()
    if not season:
        season = Season(show_id=show.id, season_number=payload.season_number)
        db.add(season)
        db.flush()

    ep_id = f"ep_{uuid.uuid4().hex[:6]}"
    ep = Episode(
        id=ep_id,
        show_id=show.id,
        season_id=season.id,
        episode_number=payload.episode_number,
        episode_title=payload.episode_title,
        duration_seconds=payload.duration_seconds,
        language=payload.language,
        content_group=payload.content_group,
        status=payload.status
    )
    db.add(ep)
    try:
        db.commit()
        db.refresh(ep)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Conflict: An episode with content_group '{payload.content_group}' and language '{payload.language}' already exists."
        )
    return ep

@router.put("/episodes/{ep_id}")
def update_episode(
    ep_id: str,
    payload: EpisodeUpdate,
    db: Session = Depends(get_db),
    role: str = Depends(require_editor)
):
    ep = db.query(Episode).filter(Episode.id == ep_id).first()
    if not ep:
        raise HTTPException(status_code=404, detail="Episode not found")

    new_cg = payload.content_group if payload.content_group is not None else ep.content_group
    new_lang = payload.language if payload.language is not None else ep.language

    # If updating content_group or language, check uniqueness constraint
    if new_cg != ep.content_group or new_lang != ep.language:
        dup = db.query(Episode).filter(
            Episode.content_group == new_cg,
            Episode.language == new_lang,
            Episode.id != ep_id
        ).first()
        if dup:
            raise HTTPException(
                status_code=400,
                detail=f"Conflict: Episode '{dup.id}' already exists with content_group '{new_cg}' and language '{new_lang}'."
            )

    if payload.episode_title is not None:
        ep.episode_title = payload.episode_title
    if payload.duration_seconds is not None:
        ep.duration_seconds = payload.duration_seconds
    if payload.language is not None:
        ep.language = payload.language
    if payload.content_group is not None:
        ep.content_group = payload.content_group
    if payload.status is not None:
        ep.status = payload.status
    if payload.season_number is not None:
        season = db.query(Season).filter(
            Season.show_id == ep.show_id,
            Season.season_number == payload.season_number
        ).first()
        if not season:
            season = Season(show_id=ep.show_id, season_number=payload.season_number)
            db.add(season)
            db.flush()
        ep.season_id = season.id

    try:
        db.commit()
        db.refresh(ep)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Conflict: An episode with content_group '{new_cg}' and language '{new_lang}' already exists."
        )
    return ep

# --- ARTWORK UPLOAD ---

@router.post("/episodes/{ep_id}/artwork")
async def upload_episode_artwork(
    ep_id: str,
    artwork_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    role: str = Depends(require_editor)
):
    ep = db.query(Episode).filter(Episode.id == ep_id).first()
    if not ep:
        raise HTTPException(status_code=404, detail="Episode not found")

    file_bytes = await file.read()

    # Validate image properties & aspect ratio using Pillow validator
    try:
        width, height, size_kb = validate_artwork(file_bytes, artwork_type, file.filename)
    except ArtworkValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)

    storage = get_storage()
    ext = os.path.splitext(file.filename or "image.jpg")[1] or ".jpg"
    key = f"artworks/{ep_id}_{artwork_type}{ext}"
    
    file_path = storage.save(key, file_bytes)
    url = storage.get_url(key)

    # Check if artwork entry exists
    art = db.query(Artwork).filter(
        Artwork.episode_id == ep_id,
        Artwork.artwork_type == artwork_type
    ).first()

    if not art:
        art = Artwork(
            episode_id=ep_id,
            artwork_type=artwork_type,
            file_path=file_path,
            url=url,
            width=width,
            height=height,
            file_size_kb=size_kb
        )
        db.add(art)
    else:
        art.file_path = file_path
        art.url = url
        art.width = width
        art.height = height
        art.file_size_kb = size_kb

    db.commit()
    db.refresh(art)

    return {
        "message": "Artwork uploaded successfully",
        "artwork": {
            "id": art.id,
            "episode_id": art.episode_id,
            "artwork_type": art.artwork_type,
            "url": art.url,
            "width": art.width,
            "height": art.height,
            "file_size_kb": art.file_size_kb
        }
    }

# --- VALIDATION REPORT & PUBLISH ---

@router.get("/validation-report")
def get_validation_report(
    db: Session = Depends(get_db),
    role: str = Depends(require_editor)
):
    return generate_validation_report(db)

@router.post("/catalog/publish")
def trigger_publish_catalog(
    db: Session = Depends(get_db),
    role: str = Depends(require_admin) # STRICTLY REQUIRE ADMIN ROLE
):
    try:
        run_record = execute_catalog_publish(db, published_by=role)
        return {
            "status": "success",
            "message": "Catalog published successfully",
            "run_id": run_record.id,
            "published_at": run_record.published_at,
            "item_counts": run_record.item_counts
        }
    except PublishBlockedError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Publish blocked by validation errors",
                "validation_report": e.report
            }
        )

@router.get("/publish-runs")
def get_publish_runs(
    db: Session = Depends(get_db),
    role: str = Depends(require_editor)
):
    runs = db.query(PublishRun).order_by(PublishRun.published_at.desc()).limit(20).all()
    return [
        {
            "id": r.id,
            "published_at": r.published_at,
            "published_by": r.published_by,
            "status": r.status,
            "item_counts": r.item_counts,
            "error_summary": r.error_summary
        }
        for r in runs
    ]
