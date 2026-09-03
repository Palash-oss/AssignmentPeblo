import os
import json
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.show import Show, Season, Episode, Artwork
from app.core.config import settings

def get_allowed_sections() -> List[str]:
    ref_path = os.path.join(settings.SEED_DATA_DIR, "reference.json")
    if os.path.exists(ref_path):
        try:
            with open(ref_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("sections", ["featured", "series", "minisodes", "songs"])
        except Exception:
            pass
    return ["featured", "series", "minisodes", "songs"]

def generate_validation_report(
    db: Session,
    seed_file_path: Optional[str] = None,
    include_seed_file_scan: bool = True
) -> Dict[str, Any]:
    allowed_sections = get_allowed_sections()

    missing_artwork_issues = []
    missing_duration_issues = []
    missing_section_issues = []
    duplicate_content_group_issues = []

    # 1. Audit DB episodes
    episodes = db.query(Episode).all()

    for ep in episodes:
        show = ep.show
        show_title = show.title if show else "Unknown Show"

        if ep.status == "published":
            # Check Artwork
            existing_art_types = {art.artwork_type for art in ep.artworks}
            
            # Trailers (Season 0) only require thumbnail artwork; regular episodes require all 3
            if ep.season and ep.season.season_number == 0:
                required_types = {"thumbnail"}
            else:
                required_types = {"poster", "banner", "thumbnail"}

            missing_types = required_types - existing_art_types
            if missing_types:
                missing_artwork_issues.append({
                    "episode_id": ep.id,
                    "show_title": show_title,
                    "episode_title": ep.episode_title,
                    "missing_artwork": list(sorted(missing_types)),
                    "message": f"Episode '{ep.id}' ({ep.episode_title}) in '{show_title}' is published but missing required artwork: {', '.join(sorted(missing_types))}."
                })

            # Check Duration
            if ep.duration_seconds is None or ep.duration_seconds <= 0:
                missing_duration_issues.append({
                    "episode_id": ep.id,
                    "show_title": show_title,
                    "episode_title": ep.episode_title,
                    "message": f"Episode '{ep.id}' ({ep.episode_title}) in '{show_title}' is published but missing duration_seconds."
                })

    # 2. Audit Shows with published episodes for missing/invalid section
    shows = db.query(Show).all()
    for show in shows:
        published_eps = [e for e in show.episodes if e.status == "published"]
        if published_eps and (not show.section or show.section not in allowed_sections):
            missing_section_issues.append({
                "show_id": show.id,
                "show_title": show.title,
                "section": show.section,
                "published_episodes_count": len(published_eps),
                "message": f"Show '{show.title}' has {len(published_eps)} published episode(s) but has an invalid or missing section (current: '{show.section}'). Allowed sections: {', '.join(allowed_sections)}."
            })

    # 3. Audit duplicate content_group & language in DB
    seen_cg_lang: Dict[Tuple[str, str], List[str]] = {}
    for ep in episodes:
        key = (ep.content_group, ep.language)
        seen_cg_lang.setdefault(key, []).append(ep.id)

    for (cg, lang), ep_ids in seen_cg_lang.items():
        if len(ep_ids) > 1:
            duplicate_content_group_issues.append({
                "content_group": cg,
                "language": lang,
                "episode_ids": ep_ids,
                "message": f"Duplicate (content_group, language) constraint violation: content_group '{cg}' with language '{lang}' is shared by episodes {', '.join(ep_ids)}."
            })

    # Also inspect seed_shows.json directly if requested to report raw file collisions (ep_0004 & ep_9001)
    if include_seed_file_scan:
        seed_path = seed_file_path or os.path.join(settings.SEED_DATA_DIR, "seed_shows.json")
        if os.path.exists(seed_path):
            try:
                with open(seed_path, "r", encoding="utf-8") as f:
                    raw_items = json.load(f)
                    raw_seen: Dict[Tuple[str, str], List[Tuple[str, str]]] = {}
                    for item in raw_items:
                        ep_id = item.get("episode_id")
                        cg = item.get("content_group")
                        lang = item.get("language")
                        if cg and lang:
                            key = (cg, lang)
                            raw_seen.setdefault(key, []).append((ep_id, item.get("show_title")))
                    
                    for (cg, lang), ep_list in raw_seen.items():
                        if len(ep_list) > 1:
                            ep_ids = [e[0] for e in ep_list]
                            shows_str = ", ".join(list({e[1] for e in ep_list}))
                            if not any(issue["content_group"] == cg and issue["language"] == lang for issue in duplicate_content_group_issues):
                                duplicate_content_group_issues.append({
                                    "content_group": cg,
                                    "language": lang,
                                    "episode_ids": ep_ids,
                                    "shows": shows_str,
                                    "message": f"Duplicate (content_group, language) seed collision: content_group '{cg}' with language '{lang}' is shared by episodes {', '.join(ep_ids)} in seed file."
                                })
            except Exception:
                pass

    total_issues = (
        len(missing_artwork_issues) +
        len(missing_duration_issues) +
        len(missing_section_issues) +
        len(duplicate_content_group_issues)
    )

    return {
        "is_publishable": total_issues == 0,
        "total_issues": total_issues,
        "issues_by_category": {
            "missing_artwork": missing_artwork_issues,
            "missing_duration": missing_duration_issues,
            "missing_section": missing_section_issues,
            "duplicate_content_group_language": duplicate_content_group_issues,
        }
    }
