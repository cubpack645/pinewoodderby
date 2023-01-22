import logging

from django.conf import settings

from derby.core.models import Classes, Rounds, Ranks
from derby.core.common import (
    step,
    create_race_roster,
    create_heats,
    create_race_chart,
    select_racers_from_race_results,
    mark_prelims_to_ignore,
)
from derby.commands.base_round import BaseRoundCommand

logger = logging.getLogger(__name__)


STEPS = []


class Command(BaseRoundCommand):
    def __init__(self, args):
        self.name = __name__.split(".")[-1]
        self.steps = STEPS
        super().__init__(args)

    @step
    def create_racers(self):
        # see method docs for why we do this
        mark_prelims_to_ignore()

        prelims_class = Classes.objects.get(
            pk=settings.ROUND_CONFIG["prelims"]["class_id"]
        )
        prelims_round = Rounds.objects.get(
            pk=settings.ROUND_CONFIG["prelims"]["round_id"]
        )
        prelims_ranks_ex_siblings = Ranks.objects.filter(classid=prelims_class).exclude(
            rank__in=(settings.SIBLINGS, settings.PARENTS)
        )
        logger.debug(
            "Pack Slowest ranks are:\n{}".format(
                "\n".join(str(o) for o in prelims_ranks_ex_siblings)
            )
        )
        self.racers = []
        for i, racer in enumerate(
            select_racers_from_race_results(
                prelims_class,
                prelims_round,
                ranks=prelims_ranks_ex_siblings,
                select="slowest",
                limit=self.config["count"],
                average=True,
                must_complete_rounds=2,
            )
        ):
            pk = self.config["registrationinfo_id_range"].start + i
            obj = racer.clone_for_class_and_rank(pk, self.parent_class, self.ranks[0])
            obj.save()
            obj.finishtime = racer.finishtime
            self.racers.append(obj)
        create_race_roster(
            self.racers, parent_class=self.parent_class, round=self.round
        )

    @step
    def schedule(self):
        logger.info(f"Allocating {len(self.racers)} racers to heats for Pack Slowest")
        for i, racer in enumerate(self.racers, 1):
            logger.debug(f"{i:02d} {racer.finishtime:.3f} {racer}")
        heats = create_heats(self.racers, randomize=self.randomize_lanes)
        create_race_chart(
            heats,
            self.config["racechart_id_range"].start,
            self.parent_class,
            self.round,
            self.config["phase"],
        )
