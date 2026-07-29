"""Business branding — logo path and display name."""
from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
LOGO_PATH = ASSETS_DIR / "logo.png"

BUSINESS_NAME = "International Laundries"
BUSINESS_SHORT = "AFG Laundry"
BUSINESS_TAGLINE = "Professional Garment Care"


def get_logo_path() -> Path | None:
    return LOGO_PATH if LOGO_PATH.is_file() else None
