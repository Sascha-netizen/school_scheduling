from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
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
            selected_stage = Stage.objects.get(pk=stage_id)
            form = LessonForm()
            form.fields['class_group'].queryset = ClassGroup.objects.filter(stage_id=stage_id)
            form.fields['subject'].queryset = Subject.objects.filter(stage_id=stage_id)
            form.fields['room'].queryset = Room.objects.filter(stage_id=stage_id)
            form.fields['teacher'].queryset = Teacher.objects.filter(stage_id=stage_id)
            form.fields['timeslot'].queryset = TimeSlot.objects.filter(stage_id=stage_id)

        elif stage_id and 'save_lesson' in request.POST:
            selected_stage = Stage.objects.get(pk=stage_id)
            form = LessonForm(request.POST)

            form.fields['class_group'].queryset = ClassGroup.objects.filter(stage_id=stage_id)
            form.fields['subject'].queryset = Subject.objects.filter(stage_id=stage_id)
            form.fields['room'].queryset = Room.objects.filter(stage_id=stage_id)
            form.fields['teacher'].queryset = Teacher.objects.filter(stage_id=stage_id)
            form.fields['timeslot'].queryset = TimeSlot.objects.filter(stage_id=stage_id)

            if form.is_valid():
                form.save()
                messages.success(request, "Lesson added successfully!")  # ✅
                return redirect('create_schedule')

        else:
            form = LessonForm()
            for field in ['class_group', 'subject', 'room', 'teacher', 'timeslot']:
                form.fields[field].queryset = form.fields[field].queryset.none()

    else:
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
        'teachers': Teacher.objects.select_related('user', 'stage').order_by('user__last_name'),
        'class_groups': ClassGroup.objects.select_related('stage').order_by('stage', 'name'),
    })


# -------------------------
# Secretaries: edit lesson (NEW)
# -------------------------
@login_required
def edit_lesson(request, lesson_id):
    if not request.user.groups.filter(name='Secretaries').exists():
        return redirect('home')

    lesson = get_object_or_404(Lesson, pk=lesson_id)
    stage_id = lesson.class_group.stage_id

    if request.method == "POST":
        form = LessonForm(request.POST, instance=lesson)

        form.fields['class_group'].queryset = ClassGroup.objects.filter(stage_id=stage_id)
        form.fields['subject'].queryset = Subject.objects.filter(stage_id=stage_id)
        form.fields['room'].queryset = Room.objects.filter(stage_id=stage_id)
        form.fields['teacher'].queryset = Teacher.objects.filter(stage_id=stage_id)
        form.fields['timeslot'].queryset = TimeSlot.objects.filter(stage_id=stage_id)

        if form.is_valid():
            form.save()
            messages.success(request, "Lesson updated successfully!")  # ✅
            return redirect('create_schedule')

    else:
        form = LessonForm(instance=lesson)

        form.fields['class_group'].queryset = ClassGroup.objects.filter(stage_id=stage_id)
        form.fields['subject'].queryset = Subject.objects.filter(stage_id=stage_id)
        form.fields['room'].queryset = Room.objects.filter(stage_id=stage_id)
        form.fields['teacher'].queryset = Teacher.objects.filter(stage_id=stage_id)
        form.fields['timeslot'].queryset = TimeSlot.objects.filter(stage_id=stage_id)

    return render(request, "timetabling/edit_lesson.html", {
        'form': form,
        'lesson': lesson,
    })


# -------------------------
# Teachers: view schedule
# -------------------------
@login_required
def view_schedule(request):
    if not request.user.groups.filter(name='Teachers').exists():
        return redirect('home')

    lessons = Lesson.objects.filter(
        teacher__user=request.user
    ).order_by('timeslot__day', 'timeslot__start_time')

    return render(request, "timetabling/view_schedule.html", {
        'lessons': lessons,
    })


# -------------------------
# Admin: full schedule
# -------------------------
@staff_member_required
def admin_schedule(request):
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

    lesson = get_object_or_404(Lesson, pk=lesson_id)

    if request.method == "POST":
        lesson.delete()
        messages.success(request, "Lesson deleted successfully!")  # ✅
        return redirect('create_schedule')