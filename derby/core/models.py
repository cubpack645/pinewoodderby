# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AwardTypes(models.Model):
    awardtypeid = models.AutoField(db_column='AwardTypeID', primary_key=True)  # Field name made lowercase.
    awardtype = models.TextField(db_column='AwardType')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'AwardTypes'


class Awards(models.Model):
    awardid = models.AutoField(db_column='AwardID', primary_key=True)  # Field name made lowercase.
    awardname = models.TextField(db_column='AwardName')  # Field name made lowercase.
    awardtypeid = models.ForeignKey(AwardTypes, models.DO_NOTHING, db_column='AwardTypeID')  # Field name made lowercase.
    classid = models.IntegerField(db_column='ClassID', blank=True, null=True)  # Field name made lowercase.
    rankid = models.IntegerField(db_column='RankID', blank=True, null=True)  # Field name made lowercase.
    racerid = models.IntegerField(db_column='RacerID', blank=True, null=True)  # Field name made lowercase.
    sort = models.IntegerField(db_column='Sort')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Awards'


class Classes(models.Model):
    classid = models.AutoField(db_column='ClassID', primary_key=True)  # Field name made lowercase.
    class_field = models.TextField(db_column='Class', blank=True, null=True)  # Field name made lowercase. Field renamed because it was a Python reserved word.

    class Meta:
        managed = False
        db_table = 'Classes'


class CrewPositions(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    name = models.TextField(db_column='Name')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'CrewPositions'


class DriversTest(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    question = models.TextField(db_column='Question')  # Field name made lowercase.
    answer = models.TextField(db_column='Answer')  # Field name made lowercase.
    active = models.TextField(db_column='Active')  # Field name made lowercase. This field type is a guess.

    class Meta:
        managed = False
        db_table = 'DriversTest'


class RaceChart(models.Model):
    resultid = models.AutoField(db_column='ResultID', primary_key=True)  # Field name made lowercase.
    classid = models.ForeignKey(Classes, models.DO_NOTHING, db_column='ClassID')  # Field name made lowercase.
    roundid = models.ForeignKey('Rounds', models.DO_NOTHING, db_column='RoundID')  # Field name made lowercase.
    heat = models.IntegerField(db_column='Heat')  # Field name made lowercase.
    lane = models.IntegerField(db_column='Lane')  # Field name made lowercase.
    racerid = models.ForeignKey('RegistrationInfo', models.DO_NOTHING, db_column='RacerID', blank=True, null=True)  # Field name made lowercase.
    chartnumber = models.IntegerField(db_column='ChartNumber', blank=True, null=True)  # Field name made lowercase.
    finishtime = models.FloatField(db_column='FinishTime', blank=True, null=True)  # Field name made lowercase.
    finishplace = models.IntegerField(db_column='FinishPlace', blank=True, null=True)  # Field name made lowercase.
    points = models.IntegerField(db_column='Points', blank=True, null=True)  # Field name made lowercase.
    completed = models.DateTimeField(db_column='Completed', blank=True, null=True)  # Field name made lowercase.
    ignoretime = models.TextField(db_column='IgnoreTime', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    masterheat = models.IntegerField(db_column='MasterHeat', blank=True, null=True)  # Field name made lowercase.
    phase = models.IntegerField(db_column='Phase', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'RaceChart'


class RaceCrew(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    lastname = models.TextField(db_column='LastName')  # Field name made lowercase.
    firstname = models.TextField(db_column='FirstName')  # Field name made lowercase.
    positionid = models.ForeignKey(CrewPositions, models.DO_NOTHING, db_column='PositionID', blank=True, null=True)  # Field name made lowercase.
    customfield = models.TextField(db_column='CustomField', blank=True, null=True)  # Field name made lowercase.
    printed = models.TextField(db_column='Printed')  # Field name made lowercase. This field type is a guess.
    imagefile = models.TextField(db_column='ImageFile', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'RaceCrew'


class RaceInfo(models.Model):
    raceinfoid = models.AutoField(db_column='RaceInfoID', primary_key=True)  # Field name made lowercase.
    itemkey = models.TextField(db_column='ItemKey')  # Field name made lowercase.
    itemvalue = models.TextField(db_column='ItemValue', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'RaceInfo'


class Ranks(models.Model):
    rankid = models.AutoField(db_column='RankID', primary_key=True)  # Field name made lowercase.
    rank = models.TextField(db_column='Rank')  # Field name made lowercase.
    classid = models.ForeignKey(Classes, models.DO_NOTHING, db_column='ClassID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Ranks'


class RegistrationInfo(models.Model):
    racerid = models.AutoField(db_column='RacerID', primary_key=True)  # Field name made lowercase.
    carnumber = models.IntegerField(db_column='CarNumber')  # Field name made lowercase.
    carname = models.TextField(db_column='CarName', blank=True, null=False, default='')  # Field name made lowercase.
    lastname = models.TextField(db_column='LastName')  # Field name made lowercase.
    firstname = models.TextField(db_column='FirstName')  # Field name made lowercase.
    classid = models.IntegerField(db_column='ClassID', blank=True, null=False, default=0)  # Field name made lowercase.
    rankid = models.IntegerField(db_column='RankID', blank=True, null=False, default=0)
    passedinspection = models.IntegerField(db_column='PassedInspection', blank=True, null=False, default=1)
    imagefile = models.TextField(db_column='ImageFile', blank=True, null=False, default='')
    exclude = models.IntegerField(db_column='Exclude', blank=True, null=False, default=0)
    printed = models.IntegerField(db_column='Printed', blank=True, null=False, default=0)

    class Meta:
        managed = False
        db_table = 'RegistrationInfo'

    @classmethod
    def from_import(cls, record, classid=0, rankid=0):
        return cls(
            carnumber=int(record.carid),
            lastname=record.lastname,
            firstname=record.firstname,
            classid=classid,
            rankid=rankid,
            passedinspection=1,
        )

    def __str__(self):
        return f'({self.racerid}) {self.carnumber:03d} {self.lastname}, {self.firstname}'


class Roster(models.Model):
    rosterid = models.AutoField(db_column='RosterID', primary_key=True)  # Field name made lowercase.
    roundid = models.ForeignKey('Rounds', models.DO_NOTHING, db_column='RoundID')  # Field name made lowercase.
    classid = models.ForeignKey(Classes, models.DO_NOTHING, db_column='ClassID')  # Field name made lowercase.
    racerid = models.ForeignKey(RegistrationInfo, models.DO_NOTHING, db_column='RacerID')  # Field name made lowercase.
    finalist = models.IntegerField(db_column='Finalist')  # Field name made lowercase.
    grandfinalist = models.IntegerField(db_column='GrandFinalist')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Roster'


class Rounds(models.Model):
    roundid = models.AutoField(db_column='RoundID', primary_key=True)  # Field name made lowercase.
    round = models.IntegerField(db_column='Round')  # Field name made lowercase.
    classid = models.ForeignKey(Classes, models.DO_NOTHING, db_column='ClassID')  # Field name made lowercase.
    charttype = models.IntegerField(db_column='ChartType', blank=True, null=True)  # Field name made lowercase.
    phase = models.IntegerField(db_column='Phase')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Rounds'


class StandingsGroup(models.Model):
    standingsid = models.AutoField(db_column='StandingsID', primary_key=True)  # Field name made lowercase.
    finishplacefinal = models.IntegerField(db_column='FinishPlaceFinal')  # Field name made lowercase.
    finishplace = models.IntegerField(db_column='FinishPlace')  # Field name made lowercase.
    time = models.FloatField(db_column='Time', blank=True, null=True)  # Field name made lowercase.
    points = models.IntegerField(db_column='Points', blank=True, null=True)  # Field name made lowercase.
    avgtime = models.FloatField(db_column='AvgTime')  # Field name made lowercase.
    racerid = models.IntegerField(db_column='RacerID')  # Field name made lowercase.
    round = models.IntegerField(db_column='Round')  # Field name made lowercase.
    classid = models.IntegerField(db_column='ClassID')  # Field name made lowercase.
    rankid = models.IntegerField(db_column='RankID')  # Field name made lowercase.
    finishedallheats = models.BooleanField(db_column='FinishedAllHeats')  # Field name made lowercase.
    tiebreakercode = models.TextField(db_column='TieBreakerCode', blank=True, null=True)  # Field name made lowercase.
    heats = models.IntegerField(db_column='Heats')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'StandingsGroup'


class StandingsRound(models.Model):
    standingsid = models.AutoField(db_column='StandingsID', primary_key=True)  # Field name made lowercase.
    finishplacefinal = models.IntegerField(db_column='FinishPlaceFinal')  # Field name made lowercase.
    finishplace = models.IntegerField(db_column='FinishPlace')  # Field name made lowercase.
    time = models.FloatField(db_column='Time', blank=True, null=True)  # Field name made lowercase.
    points = models.TextField(db_column='Points', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    avgtime = models.FloatField(db_column='AvgTime')  # Field name made lowercase.
    racerid = models.IntegerField(db_column='RacerID')  # Field name made lowercase.
    round = models.IntegerField(db_column='Round')  # Field name made lowercase.
    classid = models.IntegerField(db_column='ClassID')  # Field name made lowercase.
    rankid = models.IntegerField(db_column='RankID')  # Field name made lowercase.
    finishedallheats = models.BooleanField(db_column='FinishedAllHeats')  # Field name made lowercase.
    tiebreakercode = models.TextField(db_column='TieBreakerCode', blank=True, null=True)  # Field name made lowercase.
    heats = models.IntegerField(db_column='Heats')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'StandingsRound'


class StandingsSubgroup(models.Model):
    standingsid = models.AutoField(db_column='StandingsID', primary_key=True)  # Field name made lowercase.
    finishplacefinal = models.IntegerField(db_column='FinishPlaceFinal')  # Field name made lowercase.
    finishplace = models.IntegerField(db_column='FinishPlace')  # Field name made lowercase.
    time = models.FloatField(db_column='Time', blank=True, null=True)  # Field name made lowercase.
    points = models.IntegerField(db_column='Points', blank=True, null=True)  # Field name made lowercase.
    avgtime = models.FloatField(db_column='AvgTime')  # Field name made lowercase.
    racerid = models.IntegerField(db_column='RacerID')  # Field name made lowercase.
    round = models.IntegerField(db_column='Round')  # Field name made lowercase.
    classid = models.IntegerField(db_column='ClassID')  # Field name made lowercase.
    rankid = models.IntegerField(db_column='RankID')  # Field name made lowercase.
    finishedallheats = models.BooleanField(db_column='FinishedAllHeats')  # Field name made lowercase.
    tiebreakercode = models.TextField(db_column='TieBreakerCode', blank=True, null=True)  # Field name made lowercase.
    heats = models.IntegerField(db_column='Heats')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'StandingsSubgroup'


class Timezones(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    value = models.TextField(db_column='Value', unique=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Timezones'


class User(models.Model):
    username = models.TextField()
    auth_key = models.TextField()
    password_hash = models.TextField()
    password_reset_token = models.TextField(blank=True, null=True)
    email = models.TextField(blank=True, null=True)
    role = models.IntegerField()
    status = models.IntegerField()
    last_login = models.IntegerField(blank=True, null=True)
    created_at = models.IntegerField()
    updated_at = models.IntegerField()
    heat_font_size = models.IntegerField(blank=True, null=True)
    schedules_font_size = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'User'
