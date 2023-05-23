from django.contrib import admin

# Register your models here.
from gateway.models import *

admin.site.register(Contest)
admin.site.register(Subscribe)
admin.site.register(Solution)
admin.site.register(Command)
admin.site.register(Tag)
admin.site.register(Task)
admin.site.register(Award)
admin.site.register(User)