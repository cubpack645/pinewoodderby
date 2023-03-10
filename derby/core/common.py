from collections import namedtuple
import functools
import logging
import random

from django.conf import settings

from derby.core.models import Classes, Ranks, Rounds, Roster, RaceChart

logger = logging.getLogger(__name__)

CarLane = namedtuple("CarLane", "car lane")


def create_heats(racers, randomize=True):
    heats = allocate_to_heats(racers)
    heats_with_lanes = []
    for i, heat in enumerate(heats, 1):
        heats_with_lanes.append(allocate_to_lanes(heat, randomize=randomize))
    return heats_with_lanes


def create_race_chart(heats, starting_idx, parent_class, round, phase):
    saved, skipped, populated, empty = 0, 0, 0, 0
    result_idx = starting_idx
    for heat_idx, heat in enumerate(heats, 1):
        for car_lane in heat:
            try:
                obj = RaceChart(
                    resultid=result_idx,
                    classid=parent_class,
                    round=round,
                    heat=heat_idx,
                    lane=car_lane.lane,
                    racer=car_lane.car,
                    chartnumber=0 if car_lane.car is None else car_lane.car.carnumber,
                    phase=phase,
                )
                if car_lane.car is None:
                    empty += 1
                else:
                    populated += 1
                obj.save()
                saved += 1
                result_idx += 1
            except Exception as ex:
                logger.warning(f"Failed to persist RaceChart entry with exception {ex}")
                skipped += 1
    logger.info(
        f"Saved {saved} and skipped {skipped} race chart entries, {populated} lanes filled, {empty} empty"
    )


def allocate_to_heats(
    records, lanes=settings.LANES, min_cars=settings.MIN_CARS_PER_HEAT
):
    heats = []
    remaining = records
    while remaining:
        if len(remaining) > lanes + min_cars:
            heats.append(remaining[:lanes])
            remaining = remaining[lanes:]
        elif len(remaining) <= lanes:
            heats.append(remaining)
            remaining = []
        else:
            size = len(remaining) - min_cars
            heats.append(remaining[:size])
            remaining = remaining[size:]
    return heats


def allocate_to_lanes(cars, randomize=False, lanes=settings.LANES):
    if randomize:
        cars = cars[:]
        random.shuffle(cars)
    pad_left = int((lanes - len(cars)) / 2)
    pad_right = max(lanes - pad_left - len(cars), 0)
    lanes = []
    for i in range(pad_left):
        lanes.append(CarLane(None, i + 1))
    for i, car in enumerate(cars, 1):
        lanes.append(CarLane(car, pad_left + i))
    for i in range(pad_right):
        lanes.append(CarLane(None, pad_left + len(cars) + 1 + i))
    return lanes


def create_class(class_id, class_name):
    obj = Classes(classid=class_id, class_field=class_name)
    obj.save()
    return obj


def create_ranks(names, starting_id, ending_id, parent_class):
    # first delete any existing ranks in this range
    Ranks.objects.filter(pk__gte=starting_id, pk__lte=ending_id).delete()
    ranks = []
    for i, name in enumerate(names):
        obj = Ranks(
            id=starting_id + i,
            rank=name,
            classid=parent_class,
        )
        obj.save()
        ranks.append(obj)
    return ranks


def create_round(pk, number, parent_class, chart_type, phase):
    obj = Rounds(
        id=pk,
        round=number,
        classid=parent_class,
        charttype=chart_type,
        phase=phase,
    )
    obj.save()
    return obj


def create_race_roster(racers, parent_class, round):
    for idx, racer in enumerate(racers, 1):
        obj = Roster(
            id=idx,
            classid=parent_class,
            round=round,
            racer=racer,
        )
        obj.save()


class Averager:
    def __init__(self, results):
        self.results = results

    def average(self):
        # first pass, accumulate list of times for each racer
        by_racer = {}
        for result in self.results:
            racer_result = by_racer.get(result.racer)
            if racer_result is None:
                racer_result = result
                racer_result.times = []
                by_racer[racer_result.racer] = racer_result
            if result.finishtime is not None:
                racer_result.times.append(result.finishtime)
        # second pass, average the times
        results = []
        for racer, result in by_racer.items():
            if result.times:
                result.finishtime = sum(result.times) / len(result.times)
                result.counttimes = len(result.times)
                results.append(result)
        results.sort(key=lambda i: i.finishtime)
        return results


def mark_prelims_to_ignore():
    """
    We want to exclude Siblings / Parents from Pack Slowest and Fastest rounds, to leave
    those honors for just our Scouts.
    Our own code does exactly that.
    However, in GrandPrix, its nice to be able to show Standings on screen after the Prelims
    round, so that scouts know who has made it into those rounds.  Since GrandPrix doesn't
    know to exclude the Siblings, etc, we can't show those standings as is, as they may
    include fast or slow sibling cars.
    So this method marks the siblings prelims race times as 'IgnoreTime' so that GP
    does indeed ignore them from Standings.

    This method gets called from each of the slowest, semis, finaltop2, final commands.
    Calling multiple times is redundant of course.  I considered adding this as its own
    command, and calling it just once after the prelims, but decided to keep the race
    operation as simple as possible (ie. fewer commands to have to remember).
    """
    prelims_class = Classes.objects.get(pk=settings.ROUND_CONFIG["prelims"]["class_id"])
    for record in RaceChart.objects.filter(
        classid=prelims_class,
        racer__rank__rank__in=settings.DENS_TO_MARK_IGNORE,
        ignoretime=0,
    ).select_related("racer", "racer__rank"):
        record.ignoretime = 1
        record.save()
        logger.warn(f"Marking {record.racer} {record.finishtime} as ignoretime in GP")


def select_racers_from_race_results(
    parent_class,
    round,
    ranks=None,
    heats=None,
    select="fastest",
    limit=None,
    exclude_dnf=True,
    average=False,
    must_complete_rounds=None,
):
    filters = dict(
        classid=parent_class,
        round=round,
        racer__isnull=False,
    )
    if heats:
        if isinstance(heats, int):
            heats = [heats]
        filters["heat__in"] = heats
    if ranks:
        if isinstance(ranks, Ranks):
            ranks = [ranks]
        elif not isinstance(ranks, (list, tuple)):
            ranks = list(ranks)
        filters["racer__rank__in"] = ranks
    if exclude_dnf:
        # this little detour may seem odd...
        filters["finishtime__gte"] = settings.DNF_THRESHOLD
        excluded = (
            RaceChart.objects.filter(**filters)
            .select_related("racer")
            .order_by("finishtime")
        )
        for obj in excluded:
            logger.warn(
                f"DNF threshold exceeded for {obj.racer} with time {obj.finishtime}"
            )
        del filters["finishtime__gte"]
        # ok, detour over, back to the business at hand
        filters["finishtime__lt"] = settings.DNF_THRESHOLD

    results = (
        RaceChart.objects.filter(**filters)
        .select_related("racer")
        .order_by("finishtime")
    )

    if average:
        results = Averager(results).average()

        if must_complete_rounds is not None:
            results = [
                result
                for result in results
                if result.counttimes >= must_complete_rounds
            ]

    # now lets iterate through these in fastest or slowest order, collecting racer objects as we go
    results = iter(results) if select == "fastest" else reversed(results)
    racers, seen = [], set()
    for result in results:
        if result.racer not in seen:
            seen.add(result.racer)
            result.racer.finishtime = result.finishtime
            racers.append(result.racer)
    if limit:
        racers = racers[:limit]
    return racers


def step(fn):
    """
    Decorator which adds a method in a class to a list of STEPS to be executed
    Expects to find a STEPS container in the calling codes module scope
    """
    fn.__globals__["STEPS"].append(fn)

    @functools.wraps(fn)
    def inner(fn):
        def wrapped(*args, **kwargs):
            return fn(*args, **kwargs)

    return inner
