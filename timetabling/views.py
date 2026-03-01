from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from timetabling.models import Lesson, TimeSlot

# -------------------------
# Home page
# -------------------------
def home(request):
    user = request.user
    is_secretary = False
    is_teacher = False

    if user.is_authenticated:
        is_secretary = user.groups.filter(name='Secretaries').exists()
        is_teacher = user.groups.filter(name='Teachers').exists()

    return render(request, "timetabling/index.html", {
        'is_secretary': is_secretary,
        'is_teacher': is_teacher,
    })


# -------------------------
# Secretaries: create schedule
# -------------------------
@login_required
def create_schedule(request):
    if not request.user.groups.filter(name='Secretaries').exists():
        return redirect('home')
    return render(request, "timetabling/create_schedule.html")


# -------------------------
# Teachers: view schedule
# -------------------------
@login_required
def view_schedule(request):
    if not request.user.groups.filter(name='Teachers').exists():
        return redirect('home')
    
    # Optional: fetch lessons for this teacher
    lessons = Lesson.objects.filter(teacher__user=request.user).order_by('timeslot__day', 'timeslot__start_time')
    
    return render(request, "timetabling/view_schedule.html", {
        'lessons': lessons,
    })


# -------------------------
# Admin: full schedule
# -------------------------
@staff_member_required
def admin_schedule(request):
    """
    Admin/staff page to view the full schedule.
    Will render as an HTML table.
    """
    lessons = Lesson.objects.select_related(
        'teacher', 'subject', 'room', 'class_group', 'timeslot'
    ).order_by('timeslot__day', 'timeslot__start_time')

    return render(request, "timetabling/admin_schedule.html", {
        'lessons': lessons,
    })