import django
django.setup()      # noqa

from derby.core.models import Classes, Rounds, Ranks
from derby.core.common import select_racers_from_race_results


def main():
    parent_class = Classes.objects.get(pk=1)
    for racer in select_racers_from_race_results(
        parent_class=parent_class,
        round=Rounds.objects.get(pk=50),
        ranks=list(Ranks.objects.filter(classid=parent_class, rank='Bear')),
        select='fastest',
        limit=15,
        exclude_dnf=False,
    ):
        print(racer, '{:.3f}'.format(racer.finishtime))


if __name__ == '__main__':
    main()
