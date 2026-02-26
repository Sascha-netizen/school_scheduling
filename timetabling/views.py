from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

# Create your views here.
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

@login_required
def create_schedule(request):
    if not request.user.groups.filter(name='Secretaries').exists():
        return redirect('home')
    return render(request, "timetabling/create_schedule.html")

@login_required
def view_schedule(request):
    if not request.user.groups.filter(name='Teachers').exists():
        return redirect('home')
    return render(request, "timetabling/view_schedule.html")