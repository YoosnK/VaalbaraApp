from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('', views.tasks_list, name='tasks_list'),
    path('new/', views.new_task, name='new_task'),
    path('<int:task_id>/', views.details_task, name='task_page'),
]