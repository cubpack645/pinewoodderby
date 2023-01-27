import logging

from derby.custom_reports.den_finals_report import DenFinalsReport

logger = logging.getLogger(__name__)


class Command:
    def __init__(self, args):
        self.args = args

    def run(self):
        DenFinalsReport().run()
