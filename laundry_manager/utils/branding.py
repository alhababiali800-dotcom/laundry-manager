"""Business branding — logo path and display name."""
import os
import sys
from pathlib import Path

# PyInstaller extracts bundled read-only assets under _MEIPASS.
_APP_ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
ASSETS_DIR = _APP_ROOT / "assets"
LOGO_PATH = ASSETS_DIR / "logo.png"


def get_user_assets_dir() -> Path:
    """Return a writable per-user directory for uploaded catalog images."""
    if os.name == "nt":
        root = Path(os.environ.get("APPDATA", Path.home())) / "InternationalLaundries"
    else:
        root = Path.home() / ".international_laundries"
    path = root / "assets" / "items"
    path.mkdir(parents=True, exist_ok=True)
    return path

BUSINESS_NAME = "International Laundries"
BUSINESS_SHORT = "AFG Laundry"
BUSINESS_TAGLINE = "Professional Garment Care"


def get_logo_path() -> Path | None:
    return LOGO_PATH if LOGO_PATH.is_file() else None
