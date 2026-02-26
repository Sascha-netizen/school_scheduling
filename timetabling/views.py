from django.shortcuts import render

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