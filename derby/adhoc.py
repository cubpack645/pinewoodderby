import django
django.setup()


from derby.core.models import RegistrationInfo, Classes


for obj in RegistrationInfo.objects.all():
    print(obj.firstname, obj.lastname)
for obj in Classes.objects.all():
    print(obj.classid, obj.class_field)
