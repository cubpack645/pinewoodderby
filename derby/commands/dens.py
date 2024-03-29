import logging

from django.conf import settings

from derby.core.models import Classes, RegistrationInfo, Rounds, Ranks
from derby.core.common import (
    step,
    create_race_roster,
    create_heats,
    create_race_chart,
    select_racers_from_race_results,
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
        prelims_class = Classes.objects.get(
            pk=settings.ROUND_CONFIG["prelims"]["class_id"]
        )
        prelims_round = Rounds.objects.get(
            pk=settings.ROUND_CONFIG["prelims"]["round_id"]
        )
        prelims_ranks = {
            obj.rank: obj for obj in Ranks.objects.filter(classid=prelims_class)
        }
        rank_lookup = {rank.rank: rank for rank in self.ranks}

        racers = []
        reg_id_offset = 0
        for rank in self.ranks:
            prelims_rank = prelims_ranks[rank.rank]
            for i, racer in enumerate(
                select_racers_from_race_results(
                    prelims_class,
                    prelims_round,
                    ranks=[prelims_rank],
                    select="fastest",
                    exclude_dnf=False,
                    average=True,
                    limit=self.config["count"],
                )
            ):
                pk = self.config["registrationinfo_id_range"].start + reg_id_offset
                reg_id_offset += 1
                obj = racer.clone_for_class_and_rank(
                    pk, self.parent_class, rank_lookup[racer.rank.rank]
                )
                obj.save()
                racers.append(racer)
        create_race_roster(racers, parent_class=self.parent_class, round=self.round)

    @step
    def schedule(self):
        prelims_class = Classes.objects.get(
            pk=settings.ROUND_CONFIG["prelims"]["class_id"]
        )
        prelims_round = Rounds.objects.get(
            pk=settings.ROUND_CONFIG["prelims"]["round_id"]
        )
        prelims_ranks = {
            obj.rank: obj for obj in Ranks.objects.filter(classid=prelims_class)
        }
        racer_lookup = {
            o.carnumber: o
            for o in RegistrationInfo.objects.filter(classid=self.parent_class)
        }
        heats = []
        for rank in self.ranks:
            prelims_rank = prelims_ranks[rank.rank]
            racers = select_racers_from_race_results(
                prelims_class,
                prelims_round,
                ranks=[prelims_rank],
                select="fastest",
                exclude_dnf=False,
                average=True,
                limit=self.config["count"],
            )
            if not racers:
                logger.warn(f"No racers found for den finals for {rank.rank}")
                continue
            racers = [racer_lookup.get(o.carnumber) for o in racers]
            logger.info(f"Allocating {len(racers)} racers to heats for {rank.rank}")
            these_heats = create_heats(racers, randomize=self.randomize_lanes)
            # we had scheduled the racers to heats in fastest to slowest order
            # but for racing we want to do slowest to fastest, so reverse them here
            these_heats.reverse()
            heats.extend(these_heats)
        create_race_chart(
            heats,
            self.config["racechart_id_range"].start,
            self.parent_class,
            self.round,
            self.config["phase"],
        )
