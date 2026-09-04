import os
import json
import glob
from PIL import Image, ImageDraw, ImageFont

STORAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage", "artworks"))
SEED_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "seed_data", "seed_shows.json"))
BRAIN_DIR = r"C:\Users\Palash\.gemini\antigravity-ide\brain\f6b4f048-d5a0-4f38-8fa1-d59f490e0478"

os.makedirs(STORAGE_DIR, exist_ok=True)

def get_show_image(keyword):
    matches = glob.glob(os.path.join(BRAIN_DIR, f"*{keyword}*.png"))
    if matches:
        return matches[-1]
    return None

SHOW_IMAGE_MAP = {
    "Moti's Many Lives": get_show_image("moti_poster"),
    "Curious Cubs": get_show_image("cubs_poster"),
    "Peblo Songs": get_show_image("songs_poster"),
    "Peblo Songs — Lyrical": get_show_image("songs_poster"),
    "Discover India with Moti": get_show_image("india_poster"),
    "Tiny Tales by Banyan Dadi": get_show_image("dadi_poster"),
    "Number Nest": get_show_image("nest_poster"),
    "Rhyme Rangers": get_show_image("rangers_poster"),
}

DEFAULT_SHOW_IMG = get_show_image("moti_poster")

def crop_center(img, target_w, target_h):
    w, h = img.size
    target_aspect = target_w / float(target_h)
    img_aspect = w / float(h)

    if img_aspect > target_aspect:
        new_w = int(h * target_aspect)
        offset = (w - new_w) // 2
        crop_box = (offset, 0, offset + new_w, h)
    else:
        new_h = int(w / target_aspect)
        offset = (h - new_h) // 2
        crop_box = (0, offset, w, offset + new_h)

    cropped = img.crop(crop_box)
    return cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)

def load_font(size, bold=True):
    try:
        font_name = "arialbd.ttf" if bold else "arial.ttf"
        return ImageFont.truetype(font_name, size)
    except Exception:
        try:
            return ImageFont.truetype("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", size)
        except Exception:
            return ImageFont.load_default()

def draw_peblo_thumbnail(base_img, ep_num, ep_title, duration_sec):
    thumb = crop_center(base_img, 640, 360)
    draw = ImageDraw.Draw(thumb)

    # 1. Top Left Official Peblo Logo Badge
    draw.rectangle([20, 18, 120, 52], fill=(124, 58, 237), outline=(255, 255, 255), width=2)
    font_logo = load_font(20, bold=True)
    draw.text((32, 22), "PeBlo", fill=(255, 255, 255), font=font_logo)

    # 2. Bottom Left Off-White Peblo Card Overlay Box (matching official YouTube design)
    card_x1, card_y1, card_x2, card_y2 = 20, 220, 480, 340
    draw.rectangle([card_x1, card_y1, card_x2, card_y2], fill=(253, 252, 248), outline=(124, 58, 237), width=3)

    # Pill 1: FULL EPISODE (Purple fill)
    draw.rectangle([card_x1 + 15, card_y1 + 15, card_x1 + 145, card_y1 + 42], fill=(124, 58, 237))
    font_pill = load_font(12, bold=True)
    draw.text((card_x1 + 25, card_y1 + 20), "FULL EPISODE", fill=(255, 255, 255), font=font_pill)

    # Pill 2: EP X (Outline)
    draw.rectangle([card_x1 + 155, card_y1 + 15, card_x1 + 225, card_y1 + 42], fill=(253, 252, 248), outline=(0, 0, 0), width=2)
    draw.text((card_x1 + 168, card_y1 + 20), f"EP {ep_num}", fill=(0, 0, 0), font=font_pill)

    # Pill 3: Duration MIN (Outline)
    duration_min = round(duration_sec / 60) if duration_sec else 10
    draw.rectangle([card_x1 + 235, card_y1 + 15, card_x1 + 315, card_y1 + 42], fill=(253, 252, 248), outline=(0, 0, 0), width=2)
    draw.text((card_x1 + 245, card_y1 + 20), f"{duration_min} MIN", fill=(0, 0, 0), font=font_pill)

    # Episode Title text (Bold Black)
    font_title = load_font(20, bold=True)
    draw.text((card_x1 + 15, card_y1 + 55), ep_title, fill=(18, 18, 18), font=font_title)

    return thumb

def process_show_artworks():
    with open(SEED_FILE, "r", encoding="utf-8") as f:
        episodes = json.load(f)

    for ep in episodes:
        ep_id = ep.get("episode_id")
        show_title = ep.get("show_title", "Show")
        ep_title = ep.get("episode_title", "Episode")
        ep_num = ep.get("episode_number", 1)
        duration_sec = ep.get("duration_seconds", 600)

        img_path = SHOW_IMAGE_MAP.get(show_title) or DEFAULT_SHOW_IMG
        if not img_path or not os.path.exists(img_path):
            continue

        base_img = Image.open(img_path).convert("RGB")

        # 1. Poster (600x900)
        poster_img = crop_center(base_img, 600, 900)
        poster_path = os.path.join(STORAGE_DIR, f"{ep_id}_poster.jpg")
        poster_img.save(poster_path, "JPEG", quality=92)

        # 2. Banner (1280x720)
        banner_img = crop_center(base_img, 1280, 720)
        banner_path = os.path.join(STORAGE_DIR, f"{ep_id}_banner.jpg")
        banner_img.save(banner_path, "JPEG", quality=92)

        # 3. Official Peblo Style Thumbnail (640x360)
        thumb_img = draw_peblo_thumbnail(base_img, ep_num, ep_title, duration_sec)
        thumb_path = os.path.join(STORAGE_DIR, f"{ep_id}_thumbnail.jpg")
        thumb_img.save(thumb_path, "JPEG", quality=92)

    print(f"Successfully generated official Peblo branded artworks for {len(episodes)} episodes!")

if __name__ == "__main__":
    process_show_artworks()
