"""
The final is comprised of the 2 fastest from prelims plus top 3 from each of the 2 fastest semi-finals

This command populates the final roster and schedule TEMPORARILY with the 2 fastest from the prelims.  This
is done BEFORE the semi-finals, and the only reason is to allow us to display to the audience after the prelims
who will be competing in the semi-finals (via the semis command) and the fastest 2 9(this command)

The effect of this command will be overridden by the subsequent 'final' command which will push 8 racers into
the finals roster & schedule
"""
import logging

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
        self.name = 'final'
        self.steps = STEPS
        super().__init__(args)

    @step
    def create_racers(self):
        self.racers = []
        for i, racer in enumerate(self._get_prelims_finalists()):
            pk = self.config['registrationinfo_id_range'].start + i
            obj = racer.clone_for_class_and_rank(pk, self.parent_class, self.ranks[0])
            obj.save()
            self.racers.append(obj)
        create_race_roster(self.racers, parent_class=self.parent_class, round=self.round)

    def _get_prelims_finalists(self):
        prelims_class = Classes.objects.get(pk=settings.ROUND_CONFIG['prelims']['class_id'])
        prelims_round = Rounds.objects.get(pk=settings.ROUND_CONFIG['prelims']['round_id'])
        prelims_ranks_ex_siblings = Ranks.objects.filter(classid=prelims_class).exclude(rank__in=settings.SIBLINGS)
        racers = select_racers_from_race_results(
            prelims_class, prelims_round, ranks=prelims_ranks_ex_siblings,
            select='fastest',
            limit=2,
            average=True,
        )
        logger.debug('The following qualified direct from the prelims:')
        for i, racer in enumerate(racers, 1):
            logger.debug(f'{i:02d} {racer.finishtime:.3f} {racer}')
        return racers

    @step
    def schedule(self):
        heats = create_heats(self.racers, randomize=self.randomize_lanes)
        create_race_chart(
            heats, self.config['racechart_id_range'].start, self.parent_class, self.round, self.config['phase']
        )
