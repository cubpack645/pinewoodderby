import logging
import shutil

from django.conf import settings

from derby.core.models import RaceInfo

logger = logging.getLogger(__name__)


class Command:
    def __init__(self, args):
        self.args = args

    def run(self):
        db_path = settings.RESOURCES_DIR / f"{self.args.db}.sqlite"
        if not db_path.exists():
            raise ValueError(f"No database file found at {db_path}")
        logger.info(f"Copying database from {db_path} to {settings.LIVE_DB}")
        shutil.copyfile(src=db_path, dst=settings.LIVE_DB)
        logger.info("Copy complete")

        logger.info("Updating event title and date")
        RaceInfo.set_event_title("Pack 645 Pinewood Derby {self.args.date.year}")
        RaceInfo.set_event_date_str(self.args.date.strftime("%B %d %Y"))
