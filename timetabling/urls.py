from django.urls import path
from . import views
from . import exports

urlpatterns = [
    path('', views.home, name='home'),
    path('create_schedule/', views.create_schedule, name='create_schedule'),
    path('view_schedule/', views.view_schedule, name='view_schedule'),
    path('admin_schedule/', views.admin_schedule, name='admin_schedule'),
    path('lesson/<int:lesson_id>/edit/', views.edit_lesson, name='edit_lesson'),
    path('delete_lesson/<int:lesson_id>/', views.delete_lesson, name='delete_lesson'),
    path('schedule/export/', exports.export_schedule_csv, name='export_schedule_csv'),
    path('schedule/export/me/', exports.export_teacher_schedule_csv, name='export_teacher_schedule_csv'),
]