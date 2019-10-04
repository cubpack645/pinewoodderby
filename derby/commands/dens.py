import logging

from django.conf import settings

from derby.core.models import Classes, RegistrationInfo
from derby.core.common import (
    allocate_to_heats, allocate_to_lanes, step, create_class, create_ranks, create_round, create_race_roster
)

logger = logging.getLogger(__name__)

STEPS = []


class Command:
    def __init__(self, args):
        self.args = args
        self.config = settings.ROUND_CONFIG['dens']

    def run(self):
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
    def create_round(self):
        self.round = create_round(
            pk=self.config['round_id'], number=self.config['round_number'], parent_class=self.classid,
            chart_type=self.config['chart_type'], phase=self.config['phase'],
        )

    @step
    def create_registration_info(self):
        prelim_classid = Classes.objects.get(pk=settings.ROUND_CONFIG['prelims']['class_id'])
        prelim_racers = RegistrationInfo.objects.filter(classid=prelim_classid).select_related('rank')
        rank_lookup = {rank.rank: rank for rank in self.ranks}
        for i, racer in enumerate(prelim_racers, 0):
            pk = self.config['registration_info_firstid'] + i
            obj = racer.clone_for_class_and_rank(pk, self.classid, rank_lookup[racer.rank.rank])
            obj.save()
