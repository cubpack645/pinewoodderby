from collections import defaultdict
import random

from django.conf import settings
from django.utils import timezone

from derby.core.models import Classes, RaceChart, Rounds


class Command:
    def __init__(self, args):
        self.args = args
        self.config = settings.ROUND_CONFIG['prelims']
        self.classid = Classes.objects.get(pk=self.config['class_id'])
        self.round = Rounds.objects.get(pk=self.config['round_id'])
        self.min = 2.8
        self.max = 6.8
        self.range = self.max - self.min

    def run(self):
        results = list(RaceChart.objects.filter(classid=self.classid, round=self.round))
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
