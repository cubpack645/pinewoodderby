import argparse
from collections import namedtuple
import csv
import django
django.setup()
import logging
import os

from derby.core.models import RegistrationInfo, Ranks

logger = logging.getLogger(__name__)


FileRecord = namedtuple('FileRecord', 'carid lastname firstname group'.split())


def main(file):
    logger.info('main')
    records = []
    with open(file, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        reader.__next__()
        for row in reader:
            try:
                records.append(FileRecord(*row))
            except TypeError as ex:
                logger.error(f'Problem with row {row}, exception was {ex}')

    logger.info(f'Loaded {len(records)} records from file {file}')
    for classid in (1, 2):
        ranks = {obj.rank: obj for obj in Ranks.objects.filter(classid=classid)}
        for i, record in enumerate(records):
            obj = RegistrationInfo.from_import(record, classid=classid)
            rank = ranks.get(record.group)
            if rank is None:
                logger.warn(f'No Rank found for {record.group} for classid {classid}')
                continue
            obj.rankid = rank.rankid
            obj.save()
            print(obj)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', default=os.path.expanduser('~/Projects/PinewoodDerby/imports.tsv'))
    parser.add_argument('-v', '--verbose', action='count', default=0)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    logging.basicConfig(
        level=logging.WARN - max(2, args.verbose) * 10, format='%(asctime)s %(levelname)s %(module)s %(message)s'
    )
    main(args.file)
