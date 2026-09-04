import json
import logging
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.show import Show, Season, Episode, Artwork, PublishRun
from app.services.storage import get_storage
from app.services.validation_service import generate_validation_report

logger = logging.getLogger(__name__)

class PublishBlockedError(Exception):
    def __init__(self, validation_report: Dict[str, Any]):
        self.report = validation_report
        super().__init__("Publish job blocked by validation issues.")


def execute_catalog_publish(db: Session, published_by: str = "admin", include_seed_file_scan: bool = False) -> PublishRun:
    storage = get_storage()

    # 1. Run Validation pre-check
    report = generate_validation_report(db, include_seed_file_scan=include_seed_file_scan)
    if not report["is_publishable"]:
        # Log failed run
        run_record = PublishRun(
            published_by=published_by,
            status="failed",
            item_counts={},
            error_summary=json.dumps(report["issues_by_category"]),
            catalog_key="catalog.json"
        )
        db.add(run_record)
        db.commit()
        raise PublishBlockedError(report)

    # 2. Build Catalogue Data
    shows = db.query(Show).order_by(Show.title.asc()).all()

    sections_catalog: Dict[str, List[Dict[str, Any]]] = {}
    total_published_shows = 0
    total_published_episodes = 0
    section_counts: Dict[str, int] = {}

    for show in shows:
        # Collect published episodes for this show
        pub_episodes = [ep for ep in show.episodes if ep.status == "published"]
        if not pub_episodes:
            continue

        sec = show.section or "unassigned"

        # Separate normal episodes (season > 0) and trailers (season 0)
        normal_episodes = [ep for ep in pub_episodes if ep.season.season_number > 0]
        trailer_episodes = [ep for ep in pub_episodes if ep.season.season_number == 0]

        # Group normal episodes by season_number
        seasons_dict: Dict[int, List[Episode]] = {}
        for ep in normal_episodes:
            sn = ep.season.season_number
            seasons_dict.setdefault(sn, []).append(ep)

        # Build seasons list with collapsed content_groups
        seasons_list = []
        for sn in sorted(seasons_dict.keys()):
            eps_in_season = seasons_dict[sn]
            
            # Collapse episodes by content_group
            cg_groups: Dict[str, List[Episode]] = {}
            for ep in eps_in_season:
                cg_groups.setdefault(ep.content_group, []).append(ep)

            collapsed_episodes = []
            for cg, cg_eps in sorted(cg_groups.items(), key=lambda x: x[1][0].episode_number):
                # Pick representative episode (first one)
                rep = cg_eps[0]
                languages = sorted(list({e.language for e in cg_eps}))

                # Extract artwork
                art_dict = {}
                for art in rep.artworks:
                    art_dict[art.artwork_type] = art.url

                collapsed_episodes.append({
                    "content_group": cg,
                    "episode_number": rep.episode_number,
                    "title": rep.episode_title,
                    "duration_seconds": rep.duration_seconds,
                    "languages": languages,
                    "artwork": art_dict,
                    "episode_ids": [e.id for e in cg_eps]
                })

            seasons_list.append({
                "season_number": sn,
                "episodes": collapsed_episodes
            })

        # Process Trailers (Season 0)
        trailers_list = []
        for tr in trailer_episodes:
            art_dict = {art.artwork_type: art.url for art in tr.artworks}
            trailers_list.append({
                "episode_id": tr.id,
                "title": tr.episode_title,
                "duration_seconds": tr.duration_seconds,
                "language": tr.language,
                "artwork": art_dict
            })

        # Extract Show level artwork (from first available published episode artwork)
        show_artwork = {}
        if pub_episodes:
            for art in pub_episodes[0].artworks:
                show_artwork[art.artwork_type] = art.url

        show_data = {
            "id": show.id,
            "title": show.title,
            "slug": show.slug,
            "section": sec,
            "categories": show.categories or [],
            "synopsis": show.synopsis,
            "artwork": show_artwork,
            "seasons": seasons_list,
            "trailers": trailers_list
        }

        sections_catalog.setdefault(sec, []).append(show_data)
        total_published_shows += 1
        total_published_episodes += len(pub_episodes)
        section_counts[sec] = section_counts.get(sec, 0) + 1

    catalog_payload = {
        "published_at": datetime.utcnow().isoformat() + "Z",
        "total_shows": total_published_shows,
        "total_episodes": total_published_episodes,
        "sections": sections_catalog
    }

    catalog_json_bytes = json.dumps(catalog_payload, indent=2).encode("utf-8")

    # 3. Save ATOMICALLY to storage (staging file -> replace catalog.json)
    catalog_key = "catalog.json"
    storage.save_atomic(catalog_key, catalog_json_bytes)

    # 4. Audit Run Record
    run_record = PublishRun(
        published_by=published_by,
        status="success",
        item_counts=section_counts,
        error_summary=None,
        catalog_key=catalog_key
    )
    db.add(run_record)
    db.commit()

    return run_record
