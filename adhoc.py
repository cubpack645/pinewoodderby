import logging

from derby.core.backups import BackupHelper
from derby.utils import configure_logging


def main():
    helper = BackupHelper()
    helper.take_backup('prelims')
    helper.select_and_restore_backup()


if __name__ == '__main__':
    configure_logging(level=logging.DEBUG)
    main()
