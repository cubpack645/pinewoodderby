import logging

from django.conf import settings

from derby.core.models import RaceChart

logger = logging.getLogger(__name__)


class Command():
    def __init__(self, args):
        self.args = args

    def run(self):
        entries_to_dq = RaceChart.objects.filter(racer__carnumber__in=settings.AUTO_DQ).select_related('racer')
        for entry in entries_to_dq:
            logger.info(f'About to DQ {entry.racer}: {entry.resultid=} {entry.finishtime=} {entry.finishplace=}')
            entry.finishtime = settings.DNF_THRESHOLD + 1.0
            entry.finishplace = 100
            entry.save()
