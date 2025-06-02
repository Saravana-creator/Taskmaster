from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add/', views.add_task, name='add_task'),
    path('edit/<int:task_id>/', views.edit_task, name='edit_task'),
    path('complete/<int:task_id>/', views.complete_task, name='complete_task'),
    path('detail/<int:task_id>/', views.task_detail, name='task_detail'),
    path('all/', views.all_tasks, name='all_tasks'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('analytics/', views.analytics_view, name='analytics'),
    path('settings/', views.settings_view, name='settings'),
]
