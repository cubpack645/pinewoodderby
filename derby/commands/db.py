import logging
import os
import shutil

from django.conf import settings

logger = logging.getLogger(__name__)


class Command():
    def __init__(self, args):
        self.args = args

    def run(self):
        if self.args.pristine:
            db = 'pristine'
        elif getattr(self.args, '2019', False):
            db = '2019'
        else:
            raise Exception('Did not recognize the db you wanted to restore from')
        src = os.path.join(settings.RESOURCES_DIR, f'{db}.sqlite')
        logger.info(f'Copying database from {src} to {settings.LIVE_DB}')
        shutil.copyfile(src=src, dst=settings.LIVE_DB)
        logger.info('Copy complete')
