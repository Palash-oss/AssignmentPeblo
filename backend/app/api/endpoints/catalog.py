import json
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.db import get_db
from app.models.show import Show, Season, Episode, Artwork
from app.services.storage import get_storage

router = APIRouter(tags=["catalog"])

@router.get("/catalog")
def get_published_catalog():
    """
    Serves the published catalogue JSON direct from storage.
    Public route for Viewer UI — reads ONLY pre-published catalog.
    """
    storage = get_storage()
    catalog_key = "catalog.json"
    
    if not storage.exists(catalog_key):
        return Response(
            content=json.dumps({"published_at": None, "total_shows": 0, "total_episodes": 0, "sections": {}}),
            media_type="application/json",
            status_code=200
        )
    
    catalog_bytes = storage.read(catalog_key)
    return Response(content=catalog_bytes, media_type="application/json")


@router.get("/catalog/search")
def search_catalog(
    q: Optional[str] = Query(None, description="Search query matching show title, episode title, or category"),
    category: Optional[str] = Query(None, description="Category filter (e.g. adventure, india)"),
    language: Optional[str] = Query(None, description="Language filter (e.g. en, hi)"),
    section: Optional[str] = Query(None, description="Section filter (e.g. featured, series)"),
    db: Session = Depends(get_db)
):
    """
    Composable DB search endpoint for public Viewer UI.
    All provided filters compose with AND logic at the database query level.
    Collapses content_group variants into single results with merged languages.
    Excludes season_number 0 (trailers) from standard episode rows.
    """
    # Build DB Query joining Show, Season, Episode
    query = db.query(Episode).join(Show).join(Season).filter(Episode.status == "published")

    # Exclude Season 0 trailers from standard episode search results
    query = query.filter(Season.season_number > 0)

    # 1. Section Filter
    if section:
        query = query.filter(Show.section == section)

    # 2. Language Filter
    if language:
        query = query.filter(Episode.language == language)

    # 3. Category Filter
    if category:
        # categories stored as JSON array in SQLite/Postgres
        cat_pattern = f"%{category.lower()}%"
        query = query.filter(func.lower(Show.categories).like(cat_pattern))

    # 4. Text Query (q) matching show title, episode title, category
    if q:
        q_pattern = f"%{q.lower()}%"
        query = query.filter(
            (func.lower(Show.title).like(q_pattern)) |
            (func.lower(Episode.episode_title).like(q_pattern)) |
            (func.lower(Show.categories).like(q_pattern))
        )

    episodes = query.order_by(Show.title.asc(), Episode.episode_number.asc()).all()

    # Collapse content_group variants across matching episodes
    cg_map: Dict[str, List[Episode]] = {}
    for ep in episodes:
        cg_map.setdefault(ep.content_group, []).append(ep)

    results = []
    for cg, cg_eps in cg_map.items():
        rep = cg_eps[0]
        show = rep.show
        
        # Merge all available languages for this content_group
        all_languages = sorted(list({
            e.language for e in db.query(Episode).filter(
                Episode.content_group == cg,
                Episode.status == "published"
            ).all()
        }))

        art_dict = {a.artwork_type: a.url for a in rep.artworks}
        show_art = {}
        if show.episodes:
            show_art = {a.artwork_type: a.url for a in show.episodes[0].artworks}

        results.append({
            "content_group": cg,
            "episode_id": rep.id,
            "episode_title": rep.episode_title,
            "show_id": show.id,
            "show_title": show.title,
            "show_slug": show.slug,
            "section": show.section,
            "categories": show.categories or [],
            "synopsis": show.synopsis,
            "season_number": rep.season.season_number,
            "episode_number": rep.episode_number,
            "duration_seconds": rep.duration_seconds,
            "languages": all_languages,
            "artwork": art_dict,
            "show_artwork": show_art
        })

    return {
        "query": {
            "q": q,
            "category": category,
            "language": language,
            "section": section
        },
        "total_results": len(results),
        "results": results
    }
