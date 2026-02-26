from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create_schedule/', views.create_schedule, name='create_schedule'),
    path('view_schedule/', views.view_schedule, name='view_schedule'),
]