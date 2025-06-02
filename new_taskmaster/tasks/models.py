from django.db import models
from django.conf import settings
from django.utils import timezone

class TaskList(models.Model):
    """User-specific task lists for better organization"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#007bff')  # Hex color code
    created_at = models.DateTimeField(auto_now_add=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        unique_together = ['user', 'name']
        ordering = ['name']

    def __str__(self):
        return f"{self.user.username} - {self.name}"

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
        ('minimal', 'Minimal'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    URGENCY_CHOICES = [
        ('urgent', 'Urgent'),
        ('normal', 'Normal'),
        ('low', 'Low'),
    ]

    IMPORTANCE_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    task_list = models.ForeignKey(TaskList, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Enhanced priority system
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    urgency = models.CharField(max_length=10, choices=URGENCY_CHOICES, default='normal')
    importance = models.CharField(max_length=10, choices=IMPORTANCE_CHOICES, default='medium')

    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    ai_priority_score = models.FloatField(default=0.0)  # AI-calculated priority (0-100)

    # Additional fields for better task management
    estimated_hours = models.FloatField(null=True, blank=True, help_text="Estimated time to complete in hours")
    actual_hours = models.FloatField(null=True, blank=True, help_text="Actual time spent in hours")
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags")

    # Dependencies
    depends_on = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='dependents')

    class Meta:
        ordering = ['-ai_priority_score', '-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['ai_priority_score']),
            models.Index(fields=['due_date']),
        ]

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        if self.due_date is None:
            return False
        return self.due_date < timezone.now() and self.status != 'completed'

    @property
    def days_until_due(self):
        if self.due_date is None:
            return None
        delta = self.due_date - timezone.now()
        return delta.days

    @property
    def priority_level_numeric(self):
        """Convert priority to numeric value for calculations"""
        priority_map = {
            'critical': 5,
            'high': 4,
            'medium': 3,
            'low': 2,
            'minimal': 1
        }
        return priority_map.get(self.priority, 3)

    @property
    def urgency_level_numeric(self):
        """Convert urgency to numeric value for calculations"""
        urgency_map = {
            'urgent': 3,
            'normal': 2,
            'low': 1
        }
        return urgency_map.get(self.urgency, 2)

    @property
    def importance_level_numeric(self):
        """Convert importance to numeric value for calculations"""
        importance_map = {
            'high': 3,
            'medium': 2,
            'low': 1
        }
        return importance_map.get(self.importance, 2)
