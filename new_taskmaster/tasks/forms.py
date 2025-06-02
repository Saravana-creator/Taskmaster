from django import forms
from .models import Task, TaskList

class TaskListForm(forms.ModelForm):
    class Meta:
        model = TaskList
        fields = ['name', 'description', 'color']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'color': forms.TextInput(attrs={'type': 'color'}),
        }

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'task_list', 'due_date',
            'priority', 'urgency', 'importance', 'status',
            'estimated_hours', 'tags', 'depends_on'
        ]
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'tags': forms.TextInput(attrs={'placeholder': 'Enter tags separated by commas'}),
            'estimated_hours': forms.NumberInput(attrs={'step': '0.5', 'min': '0'}),
            'depends_on': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            # Filter task lists to user's own lists
            self.fields['task_list'].queryset = TaskList.objects.filter(user=user)

            # Filter dependencies to user's own tasks (excluding current task)
            task_queryset = Task.objects.filter(user=user, status__in=['pending', 'in_progress'])
            if self.instance and self.instance.pk:
                task_queryset = task_queryset.exclude(pk=self.instance.pk)
            self.fields['depends_on'].queryset = task_queryset

class QuickTaskForm(forms.ModelForm):
    """Simplified form for quick task creation"""
    class Meta:
        model = Task
        fields = ['title', 'due_date', 'priority']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'title': forms.TextInput(attrs={'placeholder': 'What needs to be done?'}),
        }
