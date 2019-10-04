from collections import namedtuple
import random

from django.conf import settings

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
