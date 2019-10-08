from collections import namedtuple
import csv
import logging

from derby.core.models import RegistrationInfo
from derby.core.common import step, create_race_roster, create_heats, create_race_chart
from derby.commands.base_round import BaseRoundCommand

logger = logging.getLogger(__name__)

FileRecord = namedtuple('FileRecord', 'carid lastname firstname group'.split())


STEPS = []


class Command(BaseRoundCommand):
    def __init__(self, args):
        self.name = __name__.split('.')[-1]
        self.steps = STEPS
        super().__init__(args)

    @step
    def create_racers(self):
        csv_records = self._read_csv(self.args.roster)
        logger.info(f'Loaded {len(csv_records)} records from file {self.args.roster}')

        rank_lookup = {rank.rank: rank for rank in self.ranks}
        saved, skipped = 0, 0
        start_idx = self.config['registrationinfo_id_range'].start
        racers = []
        for i, record in enumerate(csv_records):
            rank = rank_lookup.get(record.group)
            if rank is None:
                logger.warning(f'No Rank found for {record.group} for record {record}')
                skipped += 1
                continue
            obj = RegistrationInfo.from_import(start_idx + i, record, self.parent_class, rank)
            obj.save()
            racers.append(obj)
            saved += 1
        create_race_roster(racers, parent_class=self.parent_class, round=self.round)
        logger.info(f'Done with import_csv, saved {saved} and skipped {skipped} records')

    @step
    def schedule(self):
        racers = RegistrationInfo.objects.filter(classid=self.parent_class)
        # every racer needs to race twice
        racers = list(racers) * 2
        heats = create_heats(racers, randomize=self.randomize_lanes)
        create_race_chart(
            heats, self.config['racechart_id_range'].start, self.parent_class, self.round, self.config['phase']
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
        return records
