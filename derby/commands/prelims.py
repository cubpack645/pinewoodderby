from collections import namedtuple
import csv
import logging

from django.conf import settings

from derby.core.models import RegistrationInfo, RaceChart
from derby.core.common import (
    step, create_class, create_ranks, create_round, create_race_roster,
    create_heats, create_race_chart
)

logger = logging.getLogger(__name__)

FileRecord = namedtuple('FileRecord', 'carid lastname firstname group'.split())


STEPS = []


class Command:
    def __init__(self, args):
        self.args = args
        self.config = settings.ROUND_CONFIG['prelims']
        self.randomize_lanes = getattr(args, 'randomize', True)

    def run(self):
        logger.info('Starting prelims')
        for i, _step in enumerate(STEPS, 1):
            logger.info(f'Doing {_step.__name__}, step {i} of {len(STEPS)}')
            _step(self)

    @step
    def create_class(self):
        self.classid = create_class(self.config['class_id'], self.config['class_name'])

    @step
    def create_ranks(self):
        self.ranks = create_ranks(
            names=self.config['ranks'], starting_id=self.config['ranks_id_range'].start,
            ending_id=self.config['ranks_id_range'].end, parent_class=self.classid
        )

    @step
    def import_csv(self):
        logger.debug('Deleting any existing registration info objects')
        RegistrationInfo.objects.filter(
            pk__gte=self.config['registrationinfo_id_range'].start,
            pk__lte=self.config['registrationinfo_id_range'].end,
            classid=self.classid,
        ).delete()

        csv_records = self._read_csv(self.args.roster)

        rank_lookup = {rank.rank: rank for rank in self.ranks}
        saved, skipped = 0, 0
        start_idx = self.config['registrationinfo_id_range'].start
        for i, record in enumerate(csv_records):
            rank = rank_lookup.get(record.group)
            if rank is None:
                logger.warn(f'No Rank found for {record.group} for record {record}')
                skipped += 1
                continue
            obj = RegistrationInfo.from_import(start_idx + i, record, self.classid, rank)
            obj.save()
            saved += 1
        logger.info(f'Done with import_csv, saved {saved} and skipped {skipped} records')

    @step
    def create_round(self):
        self.round = create_round(
            pk=self.config['round_id'], number=self.config['round_number'], parent_class=self.classid,
            chart_type=self.config['chart_type'], phase=self.config['phase'],
        )

    @step
    def create_race_roster(self):
        racers = RegistrationInfo.objects.filter(classid=self.classid)
        create_race_roster(racers, parent_class=self.classid, round=self.round)

    @step
    def schedule(self):
        # delete any previous racechart entries
        RaceChart.objects.filter(
            pk__gte=self.config['racechart_id_range'].start,
            pk__lte=self.config['racechart_id_range'].end,
        ).delete()
        racers = RegistrationInfo.objects.filter(classid=self.classid)
        # every racer needs to race twice
        racers = list(racers) * 2
        heats = create_heats(racers, randomize=self.randomize_lanes)
        create_race_chart(
            heats, self.config['racechart_id_range'].start, self.classid, self.round, self.config['phase']
        )

    def _read_csv(self, filepath):
        records = []
        with open(filepath, 'r') as f:
            reader = csv.reader(f)
            reader.__next__()
            for row in reader:
                try:
                    records.append(FileRecord(*row))
                except TypeError as ex:
                    logger.error(f'Problem with row {row}, exception was {ex}')
        logger.info(f'Loaded {len(records)} records from file {filepath}')
        return records
