from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import Task, TaskList
from .forms import TaskForm, TaskListForm, QuickTaskForm
from .services import calculate_priority, get_task_recommendations, analyze_task_patterns
from .notifications import send_email_notification, send_sms_notification

@login_required
def dashboard(request):
    """Enhanced user dashboard showing prioritized tasks with analytics"""
    # Ensure user has a default task list
    default_list, created = TaskList.objects.get_or_create(
        user=request.user,
        name='Personal',
        defaults={'is_default': True, 'description': 'Default personal task list'}
    )

    # Get active tasks
    tasks = Task.objects.filter(user=request.user, status__in=['pending', 'in_progress'])

    # Update AI priority scores
    for task in tasks:
        task.ai_priority_score = calculate_priority(task)
        task.save(update_fields=['ai_priority_score'])

    # Sort by AI priority score (descending)
    sorted_tasks = tasks.order_by('-ai_priority_score')

    # Get completed tasks (limited to 5 most recent)
    completed_tasks = Task.objects.filter(
        user=request.user,
        status='completed'
    ).order_by('-updated_at')[:5]

    # Get overdue tasks
    overdue_tasks = [task for task in tasks if task.is_overdue]

    # Get task lists
    task_lists = TaskList.objects.filter(user=request.user)

    # Get recommendations
    recommended_tasks = get_task_recommendations(request.user, limit=3)

    # Task statistics
    stats = {
        'total_active': tasks.count(),
        'overdue': len(overdue_tasks),
        'completed_today': Task.objects.filter(
            user=request.user,
            status='completed',
            updated_at__date=timezone.now().date()
        ).count(),
        'high_priority': tasks.filter(priority__in=['critical', 'high']).count(),
    }

    return render(request, 'tasks/dashboard.html', {
        'tasks': sorted_tasks[:10],  # Show top 10 priority tasks
        'completed_tasks': completed_tasks,
        'overdue_tasks': overdue_tasks,
        'task_lists': task_lists,
        'recommended_tasks': recommended_tasks,
        'stats': stats,
    })

@login_required
def add_task(request):
    """Add a new task with enhanced features"""
    if request.method == 'POST':
        form = TaskForm(request.POST, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user

            # Set default task list if none selected
            if not task.task_list:
                default_list, _ = TaskList.objects.get_or_create(
                    user=request.user,
                    name='Personal',
                    defaults={'is_default': True, 'description': 'Default personal task list'}
                )
                task.task_list = default_list

            # Save the task first to get an ID
            task.save()

            # Save many-to-many relationships
            form.save_m2m()

            # Calculate AI priority score after saving M2M relationships
            task.ai_priority_score = calculate_priority(task)
            task.save()

            # Send notification based on user preference
            if request.user.notification_preference in ['email', 'both']:
                send_email_notification(request.user, task, 'created')
            if request.user.notification_preference in ['sms', 'both'] and request.user.phone_number:
                send_sms_notification(request.user, task, 'created')

            messages.success(request, f'Task "{task.title}" added successfully!')
            return redirect('dashboard')
    else:
        form = TaskForm(user=request.user)

    return render(request, 'tasks/add_task.html', {'form': form})

@login_required
def edit_task(request, task_id):
    """Edit an existing task with enhanced features"""
    task = get_object_or_404(Task, id=task_id, user=request.user)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.ai_priority_score = calculate_priority(task)
            task.save()

            # Save many-to-many relationships
            form.save_m2m()

            # Send notification based on user preference
            if request.user.notification_preference in ['email', 'both']:
                send_email_notification(request.user, task, 'updated')
            if request.user.notification_preference in ['sms', 'both'] and request.user.phone_number:
                send_sms_notification(request.user, task, 'updated')

            messages.success(request, f'Task "{task.title}" updated successfully!')
            return redirect('dashboard')
    else:
        form = TaskForm(instance=task, user=request.user)

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

    # Send notification based on user preference
    if request.user.notification_preference in ['email', 'both']:
        send_email_notification(request.user, task, 'completed')
    if request.user.notification_preference in ['sms', 'both'] and request.user.phone_number:
        send_sms_notification(request.user, task, 'completed')

    messages.success(request, f'Task "{task.title}" marked as completed!')
    return redirect('dashboard')

@login_required
def task_detail(request, task_id):
    """View task details"""
    task = get_object_or_404(Task, id=task_id, user=request.user)
    return render(request, 'tasks/task_detail.html', {'task': task})

@login_required
def all_tasks(request):
    """View all tasks with filtering and sorting"""
    tasks = Task.objects.filter(user=request.user).order_by('-created_at')

    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        tasks = tasks.filter(status=status_filter)

    # Filter by priority if provided
    priority_filter = request.GET.get('priority')
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        tasks = tasks.filter(title__icontains=search_query)

    context = {
        'tasks': tasks,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'search_query': search_query,
    }
    return render(request, 'tasks/all_tasks.html', context)

@login_required
def calendar_view(request):
    """Calendar view of tasks"""
    tasks = Task.objects.filter(user=request.user, due_date__isnull=False).order_by('due_date')

    # Group tasks by date
    from collections import defaultdict
    tasks_by_date = defaultdict(list)
    for task in tasks:
        date_key = task.due_date.date() if task.due_date else None
        if date_key:
            tasks_by_date[date_key].append(task)

    context = {
        'tasks': tasks,
        'tasks_by_date': dict(tasks_by_date),
    }
    return render(request, 'tasks/calendar.html', context)

@login_required
def analytics_view(request):
    """Analytics and insights view"""
    from django.db.models import Count, Avg
    from datetime import datetime, timedelta

    # Basic stats
    total_tasks = Task.objects.filter(user=request.user).count()
    completed_tasks = Task.objects.filter(user=request.user, status='completed').count()
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

    # Tasks by priority
    priority_stats = Task.objects.filter(user=request.user).values('priority').annotate(count=Count('id'))

    # Tasks by status
    status_stats = Task.objects.filter(user=request.user).values('status').annotate(count=Count('id'))

    # Recent activity (last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_tasks = Task.objects.filter(user=request.user, created_at__gte=thirty_days_ago).count()
    recent_completed = Task.objects.filter(user=request.user, status='completed', updated_at__gte=thirty_days_ago).count()

    # Average AI priority score
    avg_priority_score = Task.objects.filter(user=request.user).aggregate(avg_score=Avg('ai_priority_score'))['avg_score'] or 0

    context = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'completion_rate': round(completion_rate, 1),
        'priority_stats': priority_stats,
        'status_stats': status_stats,
        'recent_tasks': recent_tasks,
        'recent_completed': recent_completed,
        'avg_priority_score': round(avg_priority_score, 1),
    }
    return render(request, 'tasks/analytics.html', context)

@login_required
def settings_view(request):
    """User settings and preferences"""
    if request.method == 'POST':
        # Handle settings updates
        user = request.user

        # Update user preferences (you can extend this based on your User model)
        email_notifications = request.POST.get('email_notifications') == 'on'
        # Add more settings as needed

        messages.success(request, 'Settings updated successfully!')
        return redirect('settings')

    context = {
        'user': request.user,
    }
    return render(request, 'tasks/settings.html', context)
