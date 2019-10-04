from derby.core.models import RegistrationInfo


class Command:
    def __init__(self, args):
        self.args = args

    def run(self):
        racers = RegistrationInfo.objects.all()
        for racer in racers:
            print(racer)
