from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Stage(models.Model):
    """
    Represents a school stage (e.g. Middle School or High School).
    Acts as the top-level anchor for all other entities in the system.
    """
    name = models.CharField(max_length=200, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Subject(models.Model):
    """
    A subject taught at a given stage (e.g. Maths - High School).
    A subject name can be reused across stages but must be unique within one.
    """
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['stage', 'name'], name='unique_subject_per_stage')
        ]

    def __str__(self):
        return f"{self.name} ({self.stage})"


class Room(models.Model):
    """
    A physical room available for scheduling at a given stage.
    Room names must be unique within a stage.
    """
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['stage', 'name'], name='unique_room_per_stage')
        ]

    def __str__(self):
        return f"{self.name} ({self.stage})"


class ClassGroup(models.Model):
    """
    A group of students that are scheduled together (e.g. Year 10A).
    Class group names must be unique within a stage.
    """
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['stage', 'name']
        constraints = [
            models.UniqueConstraint(fields=['stage', 'name'], name='unique_classgroup_per_stage')
        ]

    def __str__(self):
        return f"{self.name} ({self.stage})"


class TimeSlot(models.Model):
    """
    A specific period on a given day within a stage's timetable.
    No two timeslots at the same stage can share the same day and time range.
    """
    DAY_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
    ]

    stage = models.ForeignKey(Stage, on_delete=models.CASCADE)
    day = models.CharField(max_length=9, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ['stage', 'day', 'start_time']
        constraints = [
            models.UniqueConstraint(
                fields=['stage', 'day', 'start_time', 'end_time'],
                name='unique_timeslot_per_stage'
            )
        ]

    def __str__(self):
        return f"{self.day} {self.start_time.strftime('%H:%M')}–{self.end_time.strftime('%H:%M')} ({self.stage})"


class Teacher(models.Model):
    """
    A teacher account linked to a Django User and assigned to a stage.
    Name and display data are sourced from the related User object.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE)

    class Meta:
        ordering = ['user__last_name', 'user__first_name']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.stage.name})"


class Lesson(models.Model):
    """
    The central scheduling record linking a teacher, subject, room, class group,
    and timeslot. Unique constraints prevent double-booking of any resource.
    """
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    class_group = models.ForeignKey(ClassGroup, on_delete=models.CASCADE)
    timeslot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)

    class Meta:
        ordering = ['timeslot', 'class_group']
        constraints = [
            models.UniqueConstraint(fields=['teacher', 'timeslot'], name='unique_teacher_timeslot'),
            models.UniqueConstraint(fields=['room', 'timeslot'], name='unique_room_timeslot'),
            models.UniqueConstraint(fields=['class_group', 'timeslot'], name='unique_classgroup_timeslot'),
        ]

    def __str__(self):
        return f"{self.subject} | {self.class_group} | {self.timeslot} | {self.teacher}"
    
    def clean(self):
        # Ensure all related entities belong to the same stage
        stages = {
            self.teacher.stage,
            self.subject.stage,
            self.room.stage,
            self.class_group.stage,
            self.timeslot.stage,
        }
        if len(stages) > 1:
            raise ValidationError("All entities must belong to the same stage!")