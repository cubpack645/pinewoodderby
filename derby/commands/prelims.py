from collections import namedtuple
import csv
import functools
import logging

from django.conf import settings

from derby.core.models import Classes, Ranks, RegistrationInfo, Rounds, RaceChart, Roster
from derby.core.common import allocate_to_heats, allocate_to_lanes

logger = logging.getLogger(__name__)

FileRecord = namedtuple('FileRecord', 'carid lastname firstname group'.split())


STEPS = []
def step(fn):
    STEPS.append(fn)
    def inner(*args, **kwargs):
        fn(*args, **kwargs)
    return inner


class Command:
    def __init__(self, args):
        self.args = args
        self.config = settings.ROUND_CONFIG['prelims']

    def run(self):
        logger.info('Starting prelims')
        for i, step in enumerate(STEPS, 1):
            logger.info(f'Doing {step.__name__}, step {i} of {len(STEPS)}')
            step(self)

    @step
    def create_class(self):
        self.classid = Classes(classid=self.config['class_id'], class_field=self.config['class_name'])
        self.classid.save()

    @step
    def create_ranks(self):
        self.ranks = {}
        for i, den in enumerate(self.config['ranks']):
            obj = Ranks(
                rankid=self.config['ranks_starting_id'] + i,
                rank=den,
                classid=self.classid,
            )
            obj.save()
            self.ranks[den] = obj

    @step
    def import_csv(self):
        csv_records = self._read_csv(self.args.roster)

        logger.debug('Deleting any existing registration info objects')
        RegistrationInfo.objects.filter(
            pk__gte=self.config['registration_info_firstid'],
            pk__lte=self.config['registration_info_lastid']
        ).delete()

        saved, skipped = 0, 0
        for i, record in enumerate(csv_records):
            rank = self.ranks.get(record.group)
            if rank is None:
                logger.warn(f'No Rank found for {record.group} for record {record}')
                skipped += 1
                continue
            obj = RegistrationInfo.from_import(record, self.classid, rank)
            obj.save()
            saved += 1
        logger.info(f'Done with import_csv, saved {saved} and skipped {skipped} records')

    @step
    def schedule(self):
        self.round = self._persist_round()
        racers = RegistrationInfo.objects.filter(classid=self.classid)
        heats = self._create_heats(racers)
        self._persist_schedule(heats)

    def _create_heats(self, racers, randomize=False):
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
                    )
                    obj.save()
                    if car_lane.car:
                        obj = Roster(
                            id=result_idx,
                            classid=self.classid,
                            round=self.round,
                            racer=car_lane.car,
                        )
                        obj.save()
                    saved += 1
                except Exception as ex:
                    logger.warning(f'Failed to persist RaceChart entry with exception {ex}')
                    skipped += 1
        logger.info(f'Saved {saved} and skipped {skipped} race chart entries')

    def _persist_round(self):
        obj = Rounds(
            id=self.config['round_id'],
            round=self.config['round'],
            classid=self.classid,
            charttype=self.config['chart_type'],
            phase=self.config['phase'],
        )
        obj.save()
        return obj

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
