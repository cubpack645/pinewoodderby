from collections import namedtuple
import csv
import logging

from django.conf import settings

from derby.core.models import RegistrationInfo, RaceChart
from derby.core.common import (
    allocate_to_heats, allocate_to_lanes, step, create_class, create_ranks, create_round, create_race_roster
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
            logger.info(f'Doing {step.__name__}, step {i} of {len(STEPS)}')
            _step(self)

    @step
    def create_class(self):
        self.classid = create_class(self.config['class_id'], self.config['class_name'])

    @step
    def create_ranks(self):
        self.ranks = create_ranks(
            names=self.config['ranks'], starting_id=self.config['ranks_starting_id'],
            ending_id=self.config['ranks_ending_id'], parent_class=self.classid
        )

    @step
    def import_csv(self):
        csv_records = self._read_csv(self.args.roster)

        logger.debug('Deleting any existing registration info objects')
        RegistrationInfo.objects.filter(
            pk__gte=self.config['registration_info_firstid'],
            pk__lte=self.config['registration_info_lastid'],
        ).delete()

        rank_lookup = {rank.rank: rank for rank in self.ranks}
        saved, skipped = 0, 0
        for i, record in enumerate(csv_records):
            rank = rank_lookup.get(record.group)
            if rank is None:
                logger.warn(f'No Rank found for {record.group} for record {record}')
                skipped += 1
                continue
            obj = RegistrationInfo.from_import(record, self.classid, rank)
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
        racers = RegistrationInfo.objects.filter(classid=self.classid)
        heats = self._create_heats(racers, randomize=self.randomize_lanes)
        self._persist_schedule(heats)

    def _create_heats(self, racers, randomize=False):
        # every racer needs to race twice
        racers = list(racers) * 2
        heats = allocate_to_heats(racers)
        heats_with_lanes = []
        for i, heat in enumerate(heats, 1):
            heats_with_lanes.append(allocate_to_lanes(heat, randomize=randomize))
        return heats_with_lanes

    def _persist_schedule(self, heats):
        saved, skipped = 0, 0
        result_idx = 0
        for heat_idx, heat in enumerate(heats, 1):
            for car_lane in heat:
                try:
                    result_idx += 1
                    obj = RaceChart(
                        resultid=result_idx,
                        classid=self.classid,
                        round=self.round,
                        heat=heat_idx,
                        lane=car_lane.lane,
                        racer=car_lane.car,
                        chartnumber=0 if car_lane.car is None else car_lane.car.carnumber,
                        phase=self.config['phase'],
                    )
                    obj.save()
                    saved += 1
                except Exception as ex:
                    logger.warning(f'Failed to persist RaceChart entry with exception {ex}')
                    skipped += 1
        logger.info(f'Saved {saved} and skipped {skipped} race chart entries')

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
