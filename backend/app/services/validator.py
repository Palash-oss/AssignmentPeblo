import io
from PIL import Image
from typing import Dict, Any, Tuple, Optional

# Specs from reference.json
ARTWORK_SPECS: Dict[str, Dict[str, Any]] = {
    "poster": {
        "aspect_name": "2:3",
        "target_aspect": 2.0 / 3.0,  # 0.6667
        "target_px": (600, 900),
        "max_kb": 200,
        "orientation_description": "portrait (taller than wide)"
    },
    "banner": {
        "aspect_name": "16:9",
        "target_aspect": 16.0 / 9.0,  # 1.7778
        "target_px": (1280, 720),
        "max_kb": 200,
        "orientation_description": "landscape (wider than tall)"
    },
    "thumbnail": {
        "aspect_name": "16:9",
        "target_aspect": 16.0 / 9.0,  # 1.7778
        "target_px": (640, 360),
        "max_kb": 200,
        "orientation_description": "landscape (wider than tall)"
    }
}

ASPECT_TOLERANCE = 0.02  # 2% aspect ratio tolerance

class ArtworkValidationError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


def validate_artwork(
    file_bytes: bytes,
    artwork_type: str,
    filename: Optional[str] = None
) -> Tuple[int, int, float]:
    """
    Validates uploaded artwork image bytes against reference specifications.
    Returns (width, height, size_kb) if valid.
    Raises ArtworkValidationError with editor-friendly message if invalid.
    """
    if artwork_type not in ARTWORK_SPECS:
        raise ArtworkValidationError(
            f"Invalid artwork type '{artwork_type}'. Allowed types are poster, banner, and thumbnail."
        )

    spec = ARTWORK_SPECS[artwork_type]
    size_kb = len(file_bytes) / 1024.0

    # 1. Size Ceiling Check
    max_kb = spec["max_kb"]
    if size_kb > max_kb:
        raise ArtworkValidationError(
            f"File size ({size_kb:.1f} KB) exceeds the maximum allowed limit of {max_kb} KB for {artwork_type} artwork."
        )

    # 2. Image Decoding Check
    try:
        image = Image.open(io.BytesIO(file_bytes))
        image.verify()
        # Re-open after verify() as per Pillow documentation
        image = Image.open(io.BytesIO(file_bytes))
    except Exception:
        raise ArtworkValidationError(
            "Uploaded file is not a valid image. Please upload a JPEG, PNG, or WebP file."
        )

    width, height = image.size
    actual_aspect = float(width) / float(height) if height > 0 else 0.0
    target_aspect = spec["target_aspect"]
    target_w, target_h = spec["target_px"]

    # 3. Orientation & Aspect Ratio Check
    aspect_diff = abs(actual_aspect - target_aspect) / target_aspect
    if aspect_diff > ASPECT_TOLERANCE:
        if artwork_type == "poster" and width > height:
            raise ArtworkValidationError(
                f"This image is landscape ({width}x{height}); posters need to be portrait, taller than wide with a 2:3 aspect ratio (target 600x900)."
            )
        elif artwork_type in ("banner", "thumbnail") and height > width:
            raise ArtworkValidationError(
                f"This image is portrait ({width}x{height}); {artwork_type} artwork needs to be landscape, wider than tall with a 16:9 aspect ratio."
            )
        else:
            raise ArtworkValidationError(
                f"Image aspect ratio does not match required {spec['aspect_name']} for {artwork_type} artwork. "
                f"Uploaded dimensions: {width}x{height}."
            )

    # 4. Pixel Dimension Check (oversized or undersized)
    if width < target_w or height < target_h:
        raise ArtworkValidationError(
            f"Image resolution ({width}x{height}) is too small; {artwork_type} artwork requires minimum dimensions of {target_w}x{target_h}."
        )

    if width > target_w or height > target_h:
        raise ArtworkValidationError(
            f"Image dimensions ({width}x{height}) exceed the required target dimensions of {target_w}x{target_h} for {artwork_type} artwork."
        )

    return width, height, round(size_kb, 2)
