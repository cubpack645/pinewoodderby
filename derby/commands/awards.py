from collections import namedtuple
import csv
import logging

from django.conf import settings

from derby.core.models import Awards, RegistrationInfo
from derby.utils import resolve_user_provided_filepath

logger = logging.getLogger(__name__)

AwardRecord = namedtuple("AwardRecord", "id name winner".split())

STEPS = []


AWARD_TYPE_DESIGN = 1

# awardid = models.AutoField(db_column='AwardID', primary_key=True)  # Field name made lowercase.
# awardname = models.TextField(db_column='AwardName')  # Field name made lowercase.
# awardtypeid = models.ForeignKey(AwardTypes, models.DO_NOTHING, db_column='AwardTypeID')
# classid = models.IntegerField(db_column='ClassID', blank=True, null=True)  # Field name made lowercase.
# rankid = models.IntegerField(db_column='RankID', blank=True, null=True)  # Field name made lowercase.
# racerid = models.IntegerField(db_column='RacerID', blank=True, null=True)  # Field name made lowercase.
# sort = models.IntegerField(db_column='Sort')  # Field name made lowercase.


class Command:
    def __init__(self, args):
        self.awards_file = resolve_user_provided_filepath(args.awards)
        self.prelims_class_id = settings.ROUND_CONFIG["prelims"]["class_id"]

    def run(self):
        self.delete_existing()
        self.create_awards()

    def delete_existing(self):
        logger.info("Deleting existing Awards")
        Awards.objects.all().delete

    def create_awards(self):
        csv_records = self._read_csv(self.awards_file)

        for record in csv_records:
            award = Awards(
                id=record.id,
                name=record.name,
                award_type_id=AWARD_TYPE_DESIGN,
                class_id=self.prelims_class_id,
                sort=record.id,
            )
            if record.winner:
                try:
                    registration = RegistrationInfo.objects.get(
                        carnumber=int(record.winner), classid=self.prelims_class_id
                    )
                    award.rank_id = registration.rank_id
                    award.racer = registration
                except RegistrationInfo.DoesNotExist:
                    logger.warn(
                        f"No Record found for winner of {record.name} award - car number was {record.winner}"
                    )
            try:
                award.save()
                logger.info(f"Saved Award {award}")
            except Exception as ex:
                logger.error(
                    f"Failed to save award record for {award.name}, exception was {ex}"
                )

    def _read_csv(self, filepath):
        records = []
        with open(filepath, "r") as f:
            reader = csv.reader(f)
            header = next(reader)
            if len(header) != 3:
                raise ValueError(
                    f"Unexpected header row of Awards file at {filepath!r}.  Expected 3 fields, found {len(header)}"
                )
            for row in reader:
                try:
                    records.append(
                        AwardRecord(id=int(row[0]), name=row[1], winner=row[2])
                    )
                except TypeError as ex:
                    logger.error(f"Problem with row {row}, exception was {ex}")
        return records
