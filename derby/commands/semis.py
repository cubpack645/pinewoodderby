"""
We will pick the fastest 18 racers from the prelims, excluding siblings
The slowest 16 of these go into 2 heats (semi-finals)

from which the fastest 3 from each semi-final will proceed to a grand-final,
joining the fastest 2 from the prelims
"""
import logging
import random

from django.conf import settings

from derby.core.models import Classes, Rounds, Ranks
from derby.core.common import (
    step, create_race_roster, create_heats, create_race_chart, select_racers_from_race_results
)
from derby.commands.base_round import BaseRoundCommand

logger = logging.getLogger(__name__)


STEPS = []


class Command(BaseRoundCommand):
    def __init__(self, args):
        self.name = __name__.split('.')[-1]
        self.steps = STEPS
        super().__init__(args)

    @step
    def create_racers(self):
        prelims_class = Classes.objects.get(pk=settings.ROUND_CONFIG['prelims']['class_id'])
        prelims_round = Rounds.objects.get(pk=settings.ROUND_CONFIG['prelims']['round_id'])
        prelims_ranks_ex_siblings = Ranks.objects.filter(classid=prelims_class).exclude(rank__in=settings.SIBLINGS)
        self.racers = []
        for i, racer in enumerate(select_racers_from_race_results(
            prelims_class, prelims_round, ranks=prelims_ranks_ex_siblings,
            select='fastest',
            limit=self.config['count'],
        )):
            pk = self.config['registrationinfo_id_range'].start + i
            obj = racer.clone_for_class_and_rank(pk, self.parent_class, self.ranks[0])
            obj.save()
            obj.finishtime = racer.finishtime
            self.racers.append(obj)
        create_race_roster(self.racers, parent_class=self.parent_class, round=self.round)

    @step
    def schedule(self):
        logger.debug(f'Pack Fastest -- the following go direct to the final:')
        for i, racer in enumerate(self.racers[:2], 1):
            logger.debug(f'{i:02d} {racer.finishtime:.3f} {racer}')
        logger.debug(f'Pack Fastest -- the following go to the semi-final:')
        for i, racer in enumerate(self.racers[2:], 1):
            logger.debug(f'{i:02d} {racer.finishtime:.3f} {racer}')
        semifinalists = self.racers[2:]
        random.shuffle(semifinalists)
        heats = create_heats(semifinalists, randomize=self.randomize_lanes)
        create_race_chart(
            heats, self.config['racechart_id_range'].start, self.parent_class, self.round, self.config['phase']
        )
