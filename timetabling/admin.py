from django.contrib import admin
from .models import Stage, Subject, Room, ClassGroup
# Register your models here.

admin.site.register(Stage)
admin.site.register(Subject)
admin.site.register(Room)
admin.site.register(ClassGroup)