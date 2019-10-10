import datetime
import logging
import os
import shutil
from termcolor import colored

from django.conf import settings

logger = logging.getLogger(__name__)

TIMESTAMP_FORMAT = '%Y%m%d-%H%M%S.%f'


class BackupHelper:
    def __init__(self):
        self.path = settings.BACKUPS_DIR
        if not os.path.exists(self.path):
            logger.info(f'Backup dir {self.path} does not exist, creating it now')
            os.makedirs(self.path)
        self.root = os.path.splitext(os.path.basename(settings.LIVE_DB))[0]
        self.actions_to_backup = {action for action in settings.BACKUP_BEFORE}

    def take_backup_if_required(self, action):
        if action in self.actions_to_backup:
            self.take_backup(action)

    def take_backup(self, action):
        fname = self.get_filename(action)
        dst = os.path.join(self.path, fname)
        src = settings.LIVE_DB
        logger.info(f'Taking backup before action {action!r}')
        logger.debug(f'Copying from {src!r} to {dst!r}')
        shutil.copyfile(src=src, dst=dst)
        # remove previous backups for this root and action
        self._delete_previous(self.root, action, exclude_filepath=dst)

    def select_and_restore_backup(self):
        entry = self.select_backup()
        if entry is not None:
            self.restore_from_backup(entry)
        else:
            logger.warning('No selection, taking no action')

    def select_backup(self):
        entries = self.list()
        entries.sort(key=lambda i: i.timestamp, reverse=True)
        msg = colored('Backups Taken ', 'blue') + colored('before', 'red') + \
                colored(' the steps named (most recent shown first)', 'blue')
        print(msg)
        for i, entry in enumerate(entries, 1):
            print(colored(f'{i:2d}: {entry.action.title():12} {entry.timestamp}', 'green'))
        raw = input(colored('Enter number of the backup you wish to restore (or no response to cancel) > ', 'blue'))
        if not raw:
            return
        try:
            i = int(raw)
            return entries[i - 1]
        except Exception as ex:
            logger.error(f'Error interpreting your response {raw!r}, exception was {ex!r}')

    def restore_from_backup(self, backup):
        if not backup.valid:
            raise ValueError(f'Backup {backup} is not valid, cannot restore from it')
        src = backup.filepath
        dst = settings.LIVE_DB
        logger.warning(f'Restoring from backup {backup}')
        logger.debug(f'Copying from {src!r} to {dst!r}')
        shutil.copyfile(src=src, dst=dst)

    def list(self):
        backups = []
        for f in os.listdir(self.path):
            entry = BackupEntry(os.path.join(self.path, f))
            if entry.valid:
                backups.append(entry)
        return backups

    def get_filename(self, action):
        return f'{self.root}_{action}_{self.timestamp}.sqlite'

    @property
    def timestamp(self):
        return datetime.datetime.now().strftime(TIMESTAMP_FORMAT)

    def _delete_previous(self, root, action, exclude_filepath):
        for entry in self.list():
            if entry.valid and entry.root == root and entry.action == action and entry.filepath != exclude_filepath:
                logger.debug(f'Deleting previous entry at {entry.filepath}')
                try:
                    os.unlink(entry.filepath)
                except (FileNotFoundError, PermissionError) as ex:
                    logger.error(f'Failed to delete file at {entry.filepath} with exception {ex!r}')


class BackupEntry:
    def __init__(self, filepath):
        self.filepath = filepath
        self.path, self.fname = os.path.dirname(filepath), os.path.basename(filepath)
        self.valid = True
        try:
            self._parse()
        except ValueError as ex:
            self.valid = False
            logger.error(f'Invalid backup entry {filepath} ... exception {ex!r}')

    def _parse(self):
        self.root, self.action, self.timestamp = None, None, None
        bits = os.path.splitext(self.fname)[0].split('_')
        if len(bits) == 3:
            try:
                ts = datetime.datetime.strptime(bits[-1], TIMESTAMP_FORMAT)
            except ValueError:
                ts = None
            if ts:
                self.root, self.action, self.timestamp = *bits[:2], ts
            else:
                raise ValueError(f'Invalid timestamp {bits[-1]} in fname {self.fname}')
        else:
            raise ValueError(f'Expected 3 bits, got {len(bits)} when parsing {self.fname}')

    def __str__(self):
        return f'{self.action.title()} {self.timestamp}'
