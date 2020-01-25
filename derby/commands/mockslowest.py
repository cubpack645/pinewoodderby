from collections import defaultdict
import random

from django.conf import settings
from django.utils import timezone

from derby.core.models import Classes, RaceChart, Rounds


class Command:
    def __init__(self, args):
        self.args = args
        self.config = settings.ROUND_CONFIG['slowest']
        self.parent_class = Classes.objects.get(pk=self.config['class_id'])
        self.round = Rounds.objects.get(pk=self.config['round_id'])
        self.min = 5.0
        self.max = 6.2
        self.range = self.max - self.min

    def run(self):
        results = list(RaceChart.objects.filter(classid=self.parent_class, round=self.round, racer__isnull=False))
        byheat = defaultdict(list)
        for result in results:
            result.finishtime = self.random_time
            result.completed = timezone.now()
            result.save()
            byheat[result.heat].append(result)
        for heat in byheat.values():
            heat.sort(key=lambda i: i.finishtime)
            for i, result in enumerate(heat, 1):
                result.points = result.finishplace = i
                result.save()

    @property
    def random_time(self):
        return self.min + random.random() * self.range
