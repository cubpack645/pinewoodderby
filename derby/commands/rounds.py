import logging

from django.conf import settings

from derby.core.common import create_class, create_ranks, create_round

logger = logging.getLogger(__name__)


class Command:
    def __init__(self, args):
        self.args = args

    def run(self):
        for name, config in settings.ROUND_CONFIG.items():
            logger.info(f'Creating round config for {name}')
            self._create_round_config(name, config)

    def _create_round_config(self, name, config):
        parent_class = create_class(class_id=config['class_id'], class_name=config['class_name'])
        create_ranks(
            names=config['ranks'], starting_id=config['ranks_id_range'].start,
            ending_id=config['ranks_id_range'].end, parent_class=parent_class
        )
        create_round(
            pk=config['round_id'], number=config['round_number'], parent_class=parent_class,
            chart_type=config['chart_type'], phase=config['phase']
        )
