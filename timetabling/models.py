from django.db import models

# Create your models here.


class Stage(models.Model):
    name = models.CharField(max_length=200, unique=True)

    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    

class Subject(models.Model):
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)

    class Meta:
        ordering = ['name']
        unique_together = ('stage', 'name')
    
    def __str__(self):
        return f"{self.name} ({self.stage})"


class Room(models.Model):
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)

    class Meta:
        ordering = ['name']
        unique_together = ('stage', 'name')
    
    def __str__(self):
        return f"{self.name} ({self.stage})"


class ClassGroup(models.Model):
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('stage', 'name')  
        ordering = ['stage', 'name']

    def __str__(self):
        return f"{self.name} ({self.stage})"


class TimeSlot(models.Model):
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE)
    day = models.CharField(
        max_length=9,
        choices=[
            ('Monday', 'Monday'),
            ('Tuesday', 'Tuesday'),
            ('Wednesday', 'Wednesday'),
            ('Thursday', 'Thursday'),
            ('Friday', 'Friday'),
        ]
    )
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ['stage', 'day', 'start_time']
        unique_together = ('stage', 'day', 'start_time', 'end_time')  # no duplicate slots

    def __str__(self):
        return f"{self.day} {self.start_time.strftime('%H:%M')}–{self.end_time.strftime('%H:%M')} ({self.stage})"