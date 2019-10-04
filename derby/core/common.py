from collections import namedtuple
import random

from django.conf import settings

from derby.core.models import Classes, Ranks, RegistrationInfo, Rounds, RaceChart, Roster

CarLane = namedtuple('CarLane', 'car lane')


def allocate_to_heats(records, lanes=settings.LANES, min_cars=settings.MIN_CARS_PER_HEAT):
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


def step(fn):
    """
    Decorator which adds a method in a class to a list of STEPS to be executed
    Expects to find a STEPS container in the calling codes module scope
    """
    fn.__globals__['STEPS'].append(fn)
    def inner(fn):
        def wrapped(*args, **kwargs):
            return fn(*args, **kwargs)
    return inner
