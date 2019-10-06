import logging

from django.conf import settings

from derby.core.models import Classes, RegistrationInfo, Rounds, Ranks
from derby.core.common import (
    step, create_class, create_ranks, create_round, create_race_roster,
    create_heats, create_race_chart, select_racers_from_race_results
)

logger = logging.getLogger(__name__)

STEPS = []


class Command:
    def __init__(self, args):
        self.args = args
        self.config = settings.ROUND_CONFIG['dens']
        self.randomize_lanes = getattr(args, 'randomize', True)

    def run(self):
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

    @step
    def create_race_roster(self):
        racers = RegistrationInfo.objects.filter(classid=self.classid)
        create_race_roster(racers, parent_class=self.classid, round=self.round)

    @step
    def schedule(self):
        prelims_class = Classes.objects.get(pk=settings.ROUND_CONFIG['prelims']['class_id'])
        prelims_round = Rounds.objects.get(pk=settings.ROUND_CONFIG['prelims']['round_id'])
        heats = []
        for rank in self.ranks:
            prelims_rank = Ranks.objects.get(classid=prelims_class, rank=rank.rank)
            racers = select_racers_from_race_results(
                prelims_class, prelims_round, ranks=prelims_rank, select='fastest', exclude_dnf=False
            )
            if not racers:
                logger.warn(f'No racers found for den finals for {rank.rank}')
                continue
            # we get back the racers in fastest to slowest order
            # but we want to schedule them into heats in the opposite order, so reverse in place here
            racers.reverse()
            logger.info(f'Allocating {len(racers)} racers to heats for {rank.rank}')
            heats.extend(create_heats(racers, randomize=self.randomize_lanes))
        create_race_chart(
            heats, self.config['racechart_id_range'].start, self.classid, self.round, self.config['phase']
        )