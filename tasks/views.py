from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Task
from .forms import TaskForm
from .services import calculate_priority

@login_required
def dashboard(request):
    """User dashboard showing prioritized tasks"""
    tasks = Task.objects.filter(user=request.user, status__in=['pending', 'in_progress'])

    # Update AI priority scores
    for task in tasks:
        task.ai_priority_score = calculate_priority(task)
        task.save()

    # Sort by AI priority score (descending)
    sorted_tasks = tasks.order_by('-ai_priority_score')

    return render(request, 'tasks/dashboard.html', {
        'tasks': sorted_tasks,
    })

@login_required
def add_task(request):
    """Add a new task"""
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.ai_priority_score = calculate_priority(task)
            task.save()
            messages.success(request, 'Task added successfully!')
            return redirect('dashboard')
    else:
        form = TaskForm()

    return render(request, 'tasks/add_task.html', {'form': form})

@login_required
def edit_task(request, task_id):
    """Edit an existing task"""
    task = get_object_or_404(Task, id=task_id, user=request.user)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save(commit=False)
            task.ai_priority_score = calculate_priority(task)
            task.save()
            messages.success(request, 'Task updated successfully!')
            return redirect('dashboard')
    else:
        form = TaskForm(instance=task)

    return render(request, 'tasks/edit_task.html', {
        'form': form,
        'task': task
    })

@login_required
def complete_task(request, task_id):
    """Mark a task as completed"""
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.status = 'completed'
    task.save()
    messages.success(request, f'Task "{task.title}" marked as completed!')
    return redirect('dashboard')