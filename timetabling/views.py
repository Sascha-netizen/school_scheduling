from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from timetabling.models import Lesson, TimeSlot, Stage, ClassGroup, Subject, Room, Teacher
from .forms import LessonForm

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

    selected_stage = None
    form = None

    if request.method == "POST":
        stage_id = request.POST.get('stage')

        if stage_id and 'select_stage' in request.POST:
            # Step 1: user just picked a stage, re-render with populated form
            selected_stage = Stage.objects.get(pk=stage_id)
            form = LessonForm()
            form.fields['class_group'].queryset = ClassGroup.objects.filter(stage_id=stage_id)
            form.fields['subject'].queryset = Subject.objects.filter(stage_id=stage_id)
            form.fields['room'].queryset = Room.objects.filter(stage_id=stage_id)
            form.fields['teacher'].queryset = Teacher.objects.filter(stage_id=stage_id)
            form.fields['timeslot'].queryset = TimeSlot.objects.filter(stage_id=stage_id)

        elif stage_id and 'save_lesson' in request.POST:
            # Step 2: user submitted the full lesson form
            selected_stage = Stage.objects.get(pk=stage_id)
            form = LessonForm(request.POST)
            form.fields['class_group'].queryset = ClassGroup.objects.filter(stage_id=stage_id)
            form.fields['subject'].queryset = Subject.objects.filter(stage_id=stage_id)
            form.fields['room'].queryset = Room.objects.filter(stage_id=stage_id)
            form.fields['teacher'].queryset = Teacher.objects.filter(stage_id=stage_id)
            form.fields['timeslot'].queryset = TimeSlot.objects.filter(stage_id=stage_id)

            if form.is_valid():
                form.save()
                return redirect('create_schedule')
        else:
            # No stage selected at all
            form = LessonForm()
            for field in ['class_group', 'subject', 'room', 'teacher', 'timeslot']:
                form.fields[field].queryset = form.fields[field].queryset.none()

    else:
        # GET: blank state
        form = LessonForm()
        for field in ['class_group', 'subject', 'room', 'teacher', 'timeslot']:
            form.fields[field].queryset = form.fields[field].queryset.none()

    lessons = Lesson.objects.select_related(
        'teacher', 'subject', 'room', 'class_group', 'timeslot'
    ).order_by('timeslot__day', 'timeslot__start_time')

    return render(request, "timetabling/create_schedule.html", {
        'form': form,
        'lessons': lessons,
        'stages': Stage.objects.all(),
        'selected_stage': selected_stage,
    })


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


# -------------------------
# Secretaries: delete lesson
# -------------------------
@login_required
def delete_lesson(request, lesson_id):
    if not request.user.groups.filter(name='Secretaries').exists():
        return redirect('home')
    
    lesson = Lesson.objects.get(pk=lesson_id)
    if request.method == "POST":
        lesson.delete()
    return redirect('create_schedule')