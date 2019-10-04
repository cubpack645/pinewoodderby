import django
django.setup()          # noqa

from derby.core.models import RaceChart


def main():
    records = RaceChart.objects.filter(finishtime__isnull=False).select_related('racer')
    for record in records:
        print(record.racer.firstname, record.racer.lastname, record.finishtime)


if __name__ == '__main__':
    main()
