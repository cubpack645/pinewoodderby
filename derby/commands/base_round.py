import logging

from django.conf import settings

from derby.core.models import Classes, Ranks, Rounds, Roster, RaceChart, RegistrationInfo

logger = logging.getLogger(__name__)


class BaseRoundCommand:
    def __init__(self, args):
        self.args = args
        self.config = settings.ROUND_CONFIG.get(self.name, {})
        self._load_round_configs()
        self._cleanup_previous_entries()
        self.randomize_lanes = getattr(args, 'randomize', True)

    def run(self):
        logger.info(f'Starting {self.name}')
        for i, _step in enumerate(self.steps, 1):
            logger.info(f'Doing {_step.__name__}, step {i} of {len(self.steps)}')
            _step(self)

    def _load_round_configs(self):
        """
        set self.parent_class, self.round, self.ranks
        """
        try:
            self.parent_class = Classes.objects.get(pk=self.config['class_id'])
            self.ranks = list(Ranks.objects.filter(classid=self.parent_class).order_by('pk'))
            self.round = Rounds.objects.get(pk=self.config['round_id'])
        except Exception as ex:
            logger.error(f'Exception loading round configs for round {self.name}, exception was {ex!r}')

    def _cleanup_previous_entries(self):
        logger.info(f'Cleaning up previous for {self.name}')
        logger.debug(f'... RegistrationInfo objects')
        RegistrationInfo.objects.filter(
            pk__gte=self.config['registrationinfo_id_range'].start,
            pk__lte=self.config['registrationinfo_id_range'].end,
            classid=self.parent_class,
        ).delete()

        logger.debug(f'... Roster entries')
        Roster.objects.filter(
            classid=self.parent_class,
        ).delete()

        logger.debug(f'... RaceChart entries')
        RaceChart.objects.filter(
            pk__gte=self.config['racechart_id_range'].start,
            pk__lte=self.config['racechart_id_range'].end,
        ).delete()
