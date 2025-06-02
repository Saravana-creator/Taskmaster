from datetime import timedelta
from django.utils import timezone
from .models import Task

def calculate_priority(task):
    """
    Simple AI prioritization algorithm based on:
    1. Deadline proximity
    2. User-set priority
    3. Task age
    """
    now = timezone.now()

    # Deadline factor (0-5): closer deadline = higher score
    time_remaining = (task.due_date - now).total_seconds()
    if time_remaining <= 0:
        deadline_factor = 5  # Overdue
    elif time_remaining < 86400:  # Less than 1 day
        deadline_factor = 4
    elif time_remaining < 259200:  # Less than 3 days
        deadline_factor = 3
    elif time_remaining < 604800:  # Less than 1 week
        deadline_factor = 2
    else:
        deadline_factor = 1

    # Priority factor (1-3)
    priority_map = {'low': 1, 'medium': 2, 'high': 3}
    priority_factor = priority_map.get(task.priority, 2)

    # Age factor (0-2): older tasks get slightly higher priority
    task_age = (now - task.created_at).days
    age_factor = min(task_age / 7, 2)  # Max 2 points for tasks older than 2 weeks

    # Calculate final score (0-10 scale)
    score = (deadline_factor * 0.5) + (priority_factor * 0.3) + (age_factor * 0.2)
    normalized_score = min(score * 2, 10)  # Scale to 0-10

    return normalized_score