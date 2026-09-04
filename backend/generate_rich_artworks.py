import os
import json
import math
from PIL import Image, ImageDraw, ImageFont

STORAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage", "artworks"))
SEED_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "seed_data", "seed_shows.json"))

os.makedirs(STORAGE_DIR, exist_ok=True)

# Curated show theme palettes (gradient start, gradient end, accent color)
SHOW_PALETTES = {
    "Moti's Many Lives": ("#f59e0b", "#d97706", "#78350f"),           # Warm Golden Amber
    "Curious Cubs": ("#10b981", "#059669", "#064e3b"),                # Emerald Nature
    "Peblo Songs": ("#ec4899", "#8b5cf6", "#4c1d95"),                 # Vibrant Music Purple/Pink
    "Peblo Songs — Lyrical": ("#f43f5e", "#a855f7", "#581c87"),       # Coral Lyrical
    "Discover India with Moti": ("#ff9933", "#138808", "#000080"),    # Tricolor India
    "Tiny Tales by Banyan Dadi": ("#6366f1", "#4f46e5", "#1e1b4b"),   # Story Night Indigo
    "Number Nest": ("#0284c7", "#0369a1", "#0c4a6e"),                 # Sky Blue Math
    "Rhyme Rangers": ("#ef4444", "#dc2626", "#7f1d1d"),               # Ranger Red
}

DEFAULT_PALETTE = ("#6366f1", "#4338ca", "#1e1b4b")

def draw_gradient(draw, width, height, color1_hex, color2_hex):
    # Convert hex to RGB
    c1 = tuple(int(color1_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    c2 = tuple(int(color2_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    
    for y in range(height):
        ratio = y / float(height)
        r = int(c1[0] * (1 - ratio) + c2[0] * ratio)
        g = int(c1[1] * (1 - ratio) + c2[1] * ratio)
        b = int(c1[2] * (1 - ratio) + c2[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

def draw_decorations(draw, width, height, seed_num):
    # Draw artistic geometric patterns based on seed_num
    for i in range(5):
        cx = (seed_num * 137 + i * 190) % width
        cy = (seed_num * 89 + i * 140) % height
        radius = 40 + (i * 15)
        opacity = 30 + (i * 10)
        draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], outline=(255, 255, 255, opacity), width=3)

def create_poster(show_title: str, ep_id: str, ep_index: int) -> Image.Image:
    w, h = 600, 900
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)

    palette = SHOW_PALETTES.get(show_title, DEFAULT_PALETTE)
    draw_gradient(draw, w, h, palette[0], palette[1])
    draw_decorations(draw, w, h, ep_index)

    # Decorative header & badge
    draw.rectangle([40, 40, w - 40, 100], fill=(0, 0, 0, 80), outline=(255, 255, 255, 100), width=2)
    draw.text((60, 60), "PEBLO TV ORIGINAL", fill=(255, 255, 255))

    # Show Title block
    draw.rectangle([40, 650, w - 40, 840], fill=(0, 0, 0, 160))
    draw.text((60, 680), show_title.upper(), fill=(255, 255, 255))
    draw.text((60, 740), f"OFFICIAL SHOW POSTER", fill=(255, 215, 0))
    draw.text((60, 780), f"EPISODE REF: {ep_id}", fill=(200, 200, 200))

    return img

def create_banner(show_title: str, ep_title: str, ep_id: str, ep_index: int) -> Image.Image:
    w, h = 1280, 720
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)

    palette = SHOW_PALETTES.get(show_title, DEFAULT_PALETTE)
    draw_gradient(draw, w, h, palette[0], palette[1])
    draw_decorations(draw, w, h, ep_index * 3)

    # Dark overlay on left for text contrast
    draw.rectangle([0, 0, 650, h], fill=(0, 0, 0, 140))
    draw.text((80, 150), "NOW STREAMING", fill=(255, 215, 0))
    draw.text((80, 220), show_title.upper(), fill=(255, 255, 255))
    draw.text((80, 310), f"Featured Banner: {ep_title}", fill=(220, 220, 220))
    draw.text((80, 360), f"Peblo Kids Original • HD 1080p", fill=(180, 180, 180))

    return img

def create_thumbnail(show_title: str, ep_title: str, ep_num: int, ep_id: str, ep_index: int) -> Image.Image:
    w, h = 640, 360
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)

    palette = SHOW_PALETTES.get(show_title, DEFAULT_PALETTE)
    # Slightly shift colors for episode thumbnails to make each episode distinct
    draw_gradient(draw, w, h, palette[1], palette[0])
    draw_decorations(draw, w, h, ep_index * 7)

    # Episode badge & title overlay
    draw.rectangle([20, h - 120, w - 20, h - 20], fill=(0, 0, 0, 180))
    draw.rectangle([20, 20, 140, 60], fill=(229, 9, 20)) # Red Ep Tag
    draw.text((35, 30), f"EP {ep_num}", fill=(255, 255, 255))

    draw.text((40, h - 100), f"{ep_title}", fill=(255, 255, 255))
    draw.text((40, h - 60), f"{show_title}", fill=(200, 200, 200))

    return img

def main():
    if not os.path.exists(SEED_FILE):
        print(f"Seed file not found at {SEED_FILE}")
        return

    with open(SEED_FILE, "r", encoding="utf-8") as f:
        episodes = json.load(f)

    print(f"Generating unique custom artwork images for {len(episodes)} episodes...")

    for idx, ep in enumerate(episodes, start=1):
        ep_id = ep.get("episode_id")
        show_title = ep.get("show_title", "Peblo Show")
        ep_title = ep.get("episode_title", f"Episode {idx}")
        ep_num = ep.get("episode_number", idx)

        # 1. Poster
        poster_img = create_poster(show_title, ep_id, idx)
        poster_img.save(os.path.join(STORAGE_DIR, f"{ep_id}_poster.jpg"), "JPEG", quality=90)

        # 2. Banner
        banner_img = create_banner(show_title, ep_title, ep_id, idx)
        banner_img.save(os.path.join(STORAGE_DIR, f"{ep_id}_banner.jpg"), "JPEG", quality=90)

        # 3. Thumbnail
        thumb_img = create_thumbnail(show_title, ep_title, ep_num, ep_id, idx)
        thumb_img.save(os.path.join(STORAGE_DIR, f"{ep_id}_thumbnail.jpg"), "JPEG", quality=90)

    print("All unique show and episode artworks generated successfully!")

if __name__ == "__main__":
    main()
