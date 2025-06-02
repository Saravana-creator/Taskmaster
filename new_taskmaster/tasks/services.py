from datetime import timedelta
from django.utils import timezone
import math

def calculate_priority(task):
    """
    Enhanced AI prioritization algorithm based on:
    1. Deadline proximity (40% weight)
    2. Priority level (25% weight)
    3. Urgency level (20% weight)
    4. Importance level (10% weight)
    5. Task age (5% weight)

    Returns a score from 0-100
    """
    now = timezone.now()

    # 1. Deadline factor (0-40 points): closer deadline = higher score
    if task.due_date is None:
        # No deadline set - give moderate priority
        deadline_factor = 10
    else:
        time_remaining = (task.due_date - now).total_seconds()
        hours_remaining = time_remaining / 3600

        if time_remaining <= 0:
            deadline_factor = 40  # Overdue - maximum urgency
        elif hours_remaining <= 2:
            deadline_factor = 38  # Less than 2 hours
        elif hours_remaining <= 6:
            deadline_factor = 35  # Less than 6 hours
        elif hours_remaining <= 24:
            deadline_factor = 30  # Less than 1 day
        elif hours_remaining <= 72:
            deadline_factor = 25  # Less than 3 days
        elif hours_remaining <= 168:
            deadline_factor = 20  # Less than 1 week
        elif hours_remaining <= 336:
            deadline_factor = 15  # Less than 2 weeks
        elif hours_remaining <= 720:
            deadline_factor = 10  # Less than 1 month
        else:
            deadline_factor = 5   # More than 1 month

    # 2. Priority level factor (0-25 points)
    priority_factor = task.priority_level_numeric * 5  # 5-25 points

    # 3. Urgency factor (0-20 points)
    urgency_factor = task.urgency_level_numeric * 6.67  # ~7-20 points

    # 4. Importance factor (0-10 points)
    importance_factor = task.importance_level_numeric * 3.33  # ~3-10 points

    # 5. Age factor (0-5 points): older tasks get slightly higher priority
    if task.created_at is None:
        # Task not yet saved - give minimal age factor
        age_factor = 1
    else:
        task_age_hours = (now - task.created_at).total_seconds() / 3600
        if task_age_hours > 168:  # More than 1 week old
            age_factor = 5
        elif task_age_hours > 72:  # More than 3 days old
            age_factor = 3
        elif task_age_hours > 24:  # More than 1 day old
            age_factor = 2
        else:
            age_factor = 1

    # Calculate final score (0-100 scale)
    total_score = deadline_factor + priority_factor + urgency_factor + importance_factor + age_factor

    # Apply bonus/penalty modifiers
    if task.is_overdue:
        total_score += 10  # Bonus for overdue tasks

    # Check for dependencies
    if task.depends_on.filter(status__in=['pending', 'in_progress']).exists():
        total_score -= 5  # Penalty for tasks with incomplete dependencies

    # Ensure score is within bounds
    final_score = max(0, min(100, total_score))

    return round(final_score, 2)

def get_task_recommendations(user, limit=5):
    """
    Get AI-recommended tasks for the user based on various factors
    """
    from .models import Task

    # Get active tasks
    active_tasks = Task.objects.filter(
        user=user,
        status__in=['pending', 'in_progress']
    )

    # Update priority scores
    for task in active_tasks:
        task.ai_priority_score = calculate_priority(task)
        task.save(update_fields=['ai_priority_score'])

    # Get top priority tasks
    recommended_tasks = active_tasks.order_by('-ai_priority_score')[:limit]

    return recommended_tasks

def analyze_task_patterns(user):
    """
    Analyze user's task completion patterns for insights
    """
    from .models import Task
    from django.db.models import Avg, Count

    completed_tasks = Task.objects.filter(user=user, status='completed')

    analysis = {
        'total_completed': completed_tasks.count(),
        'avg_completion_time': completed_tasks.aggregate(
            avg_time=Avg('actual_hours')
        )['avg_time'] or 0,
        'priority_distribution': {},
        'completion_rate_by_priority': {},
    }

    # Priority distribution
    for priority, _ in Task.PRIORITY_CHOICES:
        count = completed_tasks.filter(priority=priority).count()
        analysis['priority_distribution'][priority] = count

    return analysis
