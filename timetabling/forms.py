# timetabling/forms.py
from django import forms
from .models import Lesson, ClassGroup, Subject, Room, Teacher, TimeSlot

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['class_group', 'subject', 'room', 'teacher', 'timeslot']

    class_group = forms.ModelChoiceField(queryset=ClassGroup.objects.none(), required=True)
    subject = forms.ModelChoiceField(queryset=Subject.objects.none(), required=True)
    room = forms.ModelChoiceField(queryset=Room.objects.none(), required=True)
    teacher = forms.ModelChoiceField(queryset=Teacher.objects.none(), required=True)
    timeslot = forms.ModelChoiceField(queryset=TimeSlot.objects.none(), required=True)