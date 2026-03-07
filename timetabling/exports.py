import csv
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from timetabling.models import Lesson


@login_required
def export_schedule_csv(request):
    if not request.user.groups.filter(name='Secretaries').exists():
        return redirect('home')

    lessons = Lesson.objects.select_related(
        'teacher__user', 'teacher__stage',
        'subject', 'room', 'class_group', 'timeslot'
    ).order_by('timeslot__day', 'timeslot__start_time')

    teacher_id = request.GET.get('teacher')
    class_group_id = request.GET.get('class_group')

    if teacher_id:
        lessons = lessons.filter(teacher__id=teacher_id)
    if class_group_id:
        lessons = lessons.filter(class_group__id=class_group_id)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="full_schedule.csv"'

    writer = csv.writer(response)
    writer.writerow(['Stage', 'Day', 'Start Time', 'End Time', 'Class Group', 'Subject', 'Room', 'Teacher'])

    if not lessons.exists():
        writer.writerow(['No lessons match the selected filters.', '', '', '', '', '', '', ''])
        return response

    for lesson in lessons:
        writer.writerow([
            lesson.teacher.stage.name,
            lesson.timeslot.day,
            lesson.timeslot.start_time.strftime('%H:%M'),
            lesson.timeslot.end_time.strftime('%H:%M'),
            lesson.class_group.name,
            lesson.subject.name,
            lesson.room.name,
            lesson.teacher.user.get_full_name() or lesson.teacher.user.username,
        ])

    return response

@login_required
def export_teacher_schedule_csv(request):
    if not request.user.groups.filter(name='Teachers').exists():
        return redirect('home')

    lessons = Lesson.objects.filter(
        teacher__user=request.user
    ).select_related(
        'teacher__user', 'teacher__stage',
        'subject', 'room', 'class_group', 'timeslot'
    ).order_by('timeslot__day', 'timeslot__start_time')

    filename = f"{slugify(request.user.username)}_schedule.csv"
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow(['Stage', 'Day', 'Start Time', 'End Time', 'Class Group', 'Subject', 'Room'])

    if not lessons.exists():
        writer.writerow(['No lessons scheduled.', '', '', '', '', '', ''])
        return response

    for lesson in lessons:
        writer.writerow([
            lesson.teacher.stage.name,
            lesson.timeslot.day,
            lesson.timeslot.start_time.strftime('%H:%M'),
            lesson.timeslot.end_time.strftime('%H:%M'),
            lesson.class_group.name,
            lesson.subject.name,
            lesson.room.name,
        ])

    return response