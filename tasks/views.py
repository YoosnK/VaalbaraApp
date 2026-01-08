from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Task
from .forms import CreateTask

# Create your views here.
@login_required(login_url='/users/login/')
def tasks_list(request):
    tasks = Task.objects.all().order_by('-creation_date')
    return render(request, 'tasks/tasks_list.html', {'tasks': tasks})

@login_required(login_url='/users/login/')
def details_task(request, task_id):
    task = Task.objects.get(id=task_id)
    return render(request, 'tasks/details_task.html', {'task': task})

@login_required(login_url='/users/login/')
def new_task(request):
    if request.method == 'POST':
        form = CreateTask(request.POST, request.FILES)
        if form.is_valid():
            task_new = form.save(commit=False)
            task_new.created_by = request.user
            task_new.creation_date = timezone.now()
            task_new.save()
            return redirect('tasks:tasks_list')
    else:
        form = CreateTask()
    return render(request, 'tasks/new_task.html', {'form': form})