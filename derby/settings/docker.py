from .base import *  # noqa

DATA_DIR = pathlib.Path("/data")

RESOURCES_DIR = DATA_DIR / "resources"
PRISTINE_DB = RESOURCES_DIR / "pristine.sqlite"

LIVE_DB = DATA_DIR / "live.sqlite"

REPORTS_DIR = DATA_DIR
BACKUPS_DIR = DATA_DIR / "backups"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": LIVE_DB,
    }
}
