import logging

from django.conf import settings

from derby.core.models import Classes, Rounds
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
        self.racers = []
        for i, racer in enumerate(self._get_semi_finalists() + self._get_prelims_finalists()):
            pk = self.config['registrationinfo_id_range'].start + i
            obj = racer.clone_for_class_and_rank(pk, self.parent_class, self.ranks[0])
            obj.save()
            self.racers.append(obj)
        create_race_roster(self.racers, parent_class=self.parent_class, round=self.round)

    def _get_semi_finalists(self):
        semis_class = Classes.objects.get(pk=settings.ROUND_CONFIG['semis']['class_id'])
        semis_round = Rounds.objects.get(pk=settings.ROUND_CONFIG['semis']['round_id'])
        racers = select_racers_from_race_results(
            semis_class, semis_round,
            select='fastest',
            limit=6,
        )
        logger.debug('The following qualified from the semi-finals:')
        for i, racer in enumerate(racers, 1):
            logger.debug(f'{i:02d} {racer.finishtime:.3f} {racer}')
        return racers

    def _get_prelims_finalists(self):
        prelims_class = Classes.objects.get(pk=settings.ROUND_CONFIG['prelims']['class_id'])
        prelims_round = Rounds.objects.get(pk=settings.ROUND_CONFIG['prelims']['round_id'])
        racers = select_racers_from_race_results(
            prelims_class, prelims_round,
            select='fastest',
            limit=2,
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
