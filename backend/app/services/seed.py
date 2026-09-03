import os
import json
import shutil
import logging
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.show import Show, Season, Episode, Artwork
from app.core.config import settings

logger = logging.getLogger(__name__)

ARTWORK_DEFAULT_SPECS = {
    "poster": {"width": 600, "height": 900, "size_kb": 9.0, "asset": "poster_good.jpg"},
    "banner": {"width": 1280, "height": 720, "size_kb": 15.0, "asset": "banner_good.jpg"},
    "thumbnail": {"width": 640, "height": 360, "size_kb": 4.0, "asset": "thumb_good.jpg"},
}

def run_seed_ingestion(db: Session, seed_file_path: Optional[str] = None):
    if not seed_file_path:
        seed_file_path = os.path.join(settings.SEED_DATA_DIR, "seed_shows.json")
    
    if not os.path.exists(seed_file_path):
        logger.warning(f"Seed file not found at {seed_file_path}")
        return {"shows": 0, "episodes": 0, "errors": [f"Seed file not found at {seed_file_path}"]}

    with open(seed_file_path, "r", encoding="utf-8") as f:
        items = json.load(f)

    # Ensure storage/artworks directory exists
    storage_artworks_dir = os.path.join(settings.STORAGE_DIR, "artworks")
    os.makedirs(storage_artworks_dir, exist_ok=True)
    assets_dir = os.path.join(settings.SEED_DATA_DIR, "assets")

    shows_map = {}
    seasons_map = {}
    seeded_episodes = 0
    errors = []

    for item in items:
        ep_id = item.get("episode_id")
        show_title = item.get("show_title")
        slug = item.get("slug")
        section = item.get("section")
        categories = item.get("categories", [])
        synopsis = item.get("synopsis")
        season_num = item.get("season_number")
        ep_num = item.get("episode_number")
        ep_title = item.get("episode_title")
        duration = item.get("duration_seconds")
        language = item.get("language")
        content_group = item.get("content_group")
        status = item.get("status", "draft")
        artwork_available = item.get("artwork_available")

        # 1. Show lookup or creation
        if show_title not in shows_map:
            db_show = db.query(Show).filter(Show.title == show_title).first()
            if not db_show:
                db_show = Show(
                    title=show_title,
                    slug=slug,
                    section=section,
                    categories=categories,
                    synopsis=synopsis
                )
                db.add(db_show)
                db.flush()
            shows_map[show_title] = db_show
        else:
            db_show = shows_map[show_title]
            if section and not db_show.section:
                db_show.section = section
                db.flush()

        # 2. Season lookup or creation
        season_key = (db_show.id, season_num)
        if season_key not in seasons_map:
            db_season = db.query(Season).filter(
                Season.show_id == db_show.id,
                Season.season_number == season_num
            ).first()
            if not db_season:
                db_season = Season(
                    show_id=db_show.id,
                    season_number=season_num
                )
                db.add(db_season)
                db.flush()
            seasons_map[season_key] = db_season
        else:
            db_season = seasons_map[season_key]

        # 3. Check for existing episode by ID
        existing_ep = db.query(Episode).filter(Episode.id == ep_id).first()
        if existing_ep:
            continue

        # Check for (content_group, language) uniqueness collision before insertion
        dup_ep = db.query(Episode).filter(
            Episode.content_group == content_group,
            Episode.language == language
        ).first()
        if dup_ep:
            msg = f"Seed error: Duplicate content_group '{content_group}' and language '{language}' for episode '{ep_id}' (collides with '{dup_ep.id}')"
            logger.error(msg)
            errors.append(msg)
            continue

        db_ep = Episode(
            id=ep_id,
            show_id=db_show.id,
            season_id=db_season.id,
            episode_number=ep_num,
            episode_title=ep_title,
            duration_seconds=duration,
            language=language,
            content_group=content_group,
            status=status
        )
        db.add(db_ep)
        db.flush()

        # 4. Artwork creation if specified & copy sample asset into storage
        if artwork_available and isinstance(artwork_available, list):
            for art_type in artwork_available:
                if art_type in ARTWORK_DEFAULT_SPECS:
                    spec = ARTWORK_DEFAULT_SPECS[art_type]
                    filename = f"{ep_id}_{art_type}.jpg"
                    dest_path = os.path.join(storage_artworks_dir, filename)
                    
                    # Copy sample image file to storage if available and not yet created
                    src_asset = os.path.join(assets_dir, spec["asset"])
                    if os.path.exists(src_asset) and not os.path.exists(dest_path):
                        shutil.copy(src_asset, dest_path)

                    art_rec = Artwork(
                        episode_id=ep_id,
                        artwork_type=art_type,
                        file_path=f"artworks/{filename}",
                        url=f"/storage/artworks/{filename}",
                        width=spec["width"],
                        height=spec["height"],
                        file_size_kb=spec["size_kb"]
                    )
                    db.add(art_rec)
            db.flush()

        seeded_episodes += 1

    db.commit()
    return {
        "shows": len(shows_map),
        "episodes": seeded_episodes,
        "errors": errors
    }
