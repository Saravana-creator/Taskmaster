from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_email_notification(user, task, notification_type):
    """Send email notification about a task"""
    subject_map = {
        'reminder': f'Reminder: Task "{task.title}" is due soon',
        'created': f'New Task Created: "{task.title}"',
        'updated': f'Task Updated: "{task.title}"',
        'completed': f'Task Completed: "{task.title}"',
    }
    
    message_map = {
        'reminder': f'Your task "{task.title}" is due on {task.due_date.strftime("%Y-%m-%d %H:%M")}.',
        'created': f'You have created a new task: "{task.title}" due on {task.due_date.strftime("%Y-%m-%d %H:%M")}.',
        'updated': f'Your task "{task.title}" has been updated.',
        'completed': f'Congratulations! You have completed the task: "{task.title}".',
    }
    
    subject = subject_map.get(notification_type, f'TaskMaster Notification: {task.title}')
    message = message_map.get(notification_type, f'Notification about your task: {task.title}')
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {user.email}: {str(e)}")
        return False

def send_sms_notification(user, task, notification_type):
    """Send SMS notification about a task (using Twilio)"""
    # This would use Twilio in a real implementation
    # For now, we'll just log the message
    message_map = {
        'reminder': f'REMINDER: Task "{task.title}" is due soon',
        'created': f'NEW TASK: "{task.title}" due on {task.due_date.strftime("%Y-%m-%d %H:%M")}',
        'updated': f'UPDATED: Task "{task.title}"',
        'completed': f'COMPLETED: Task "{task.title}"',
    }
    
    message = message_map.get(notification_type, f'TaskMaster: {task.title}')
    
    logger.info(f"Would send SMS to {user.phone_number}: {message}")
    return True
