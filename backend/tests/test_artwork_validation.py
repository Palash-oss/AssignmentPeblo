import os
import pytest
from app.services.validator import validate_artwork, ArtworkValidationError

ASSETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "seed_data", "assets"))

def test_poster_good():
    path = os.path.join(ASSETS_DIR, "poster_good.jpg")
    with open(path, "rb") as f:
        data = f.read()
    w, h, size_kb = validate_artwork(data, "poster")
    assert w == 600
    assert h == 900
    assert size_kb < 200

def test_banner_good():
    path = os.path.join(ASSETS_DIR, "banner_good.jpg")
    with open(path, "rb") as f:
        data = f.read()
    w, h, size_kb = validate_artwork(data, "banner")
    assert w == 1280
    assert h == 720
    assert size_kb < 200

def test_thumb_good():
    path = os.path.join(ASSETS_DIR, "thumb_good.jpg")
    with open(path, "rb") as f:
        data = f.read()
    w, h, size_kb = validate_artwork(data, "thumbnail")
    assert w == 640
    assert h == 360
    assert size_kb < 200

def test_poster_wrong_ratio():
    path = os.path.join(ASSETS_DIR, "poster_wrong_ratio.jpg")
    with open(path, "rb") as f:
        data = f.read()
    with pytest.raises(ArtworkValidationError) as exc_info:
        validate_artwork(data, "poster")
    assert "landscape" in exc_info.value.message.lower() or "aspect" in exc_info.value.message.lower()

def test_banner_too_big():
    path = os.path.join(ASSETS_DIR, "banner_too_big.png")
    with open(path, "rb") as f:
        data = f.read()
    with pytest.raises(ArtworkValidationError) as exc_info:
        validate_artwork(data, "banner")
    assert "exceed" in exc_info.value.message.lower() or "target" in exc_info.value.message.lower()

def test_thumb_tiny():
    path = os.path.join(ASSETS_DIR, "thumb_tiny.jpg")
    with open(path, "rb") as f:
        data = f.read()
    with pytest.raises(ArtworkValidationError) as exc_info:
        validate_artwork(data, "thumbnail")
    assert "small" in exc_info.value.message.lower() or "resolution" in exc_info.value.message.lower()
