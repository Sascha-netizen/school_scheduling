from django.contrib import admin
from .models import Stage, Subject, Room, ClassGroup, TimeSlot, Teacher, Lesson
# Register your models here.

@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'stage')
    list_filter = ('stage',)
    search_fields = ('name',)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'stage')
    list_filter = ('stage',)


@admin.register(ClassGroup)
class ClassGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'stage')
    list_filter = ('stage',)


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('day', 'start_time', 'end_time', 'stage')
    list_filter = ('stage', 'day')


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user', 'stage')
    list_filter = ('stage',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name')


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('subject', 'class_group', 'teacher', 'room', 'timeslot')
    list_filter = ('timeslot__day', 'teacher__stage')
    search_fields = (
        'subject__name',
        'class_group__name',
        'teacher__user__last_name',
    )