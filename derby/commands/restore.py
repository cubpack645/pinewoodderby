from derby.core.backups import BackupHelper


class Command:
    def __init__(self, args):
        self.args = args
        self.backups = BackupHelper()

    def run(self):
        self.backups.select_and_restore_backup()
