from django.core.mail import send_mail
from django.conf import settings
import os
from twilio.rest import Client

def send_email_notification(user_email, subject, message):
    """Send email notification about task deadline"""
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user_email],
        fail_silently=False,
    )

def send_sms_notification(phone_number, message):
    """Send SMS notification using Twilio"""
    # You'll need to set these environment variables
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    twilio_number = os.environ.get('TWILIO_PHONE_NUMBER')
    
    client = Client(account_sid, auth_token)
    client.messages.create(
        body=message,
        from_=twilio_number,
        to=phone_number
    )

def notify_user_about_task(task):
    """Send notification based on user preference"""
    user = task.user
    subject = f"TASKMASTER Reminder: '{task.title}' is due soon"
    message = f"Your task '{task.title}' is due on {task.deadline.strftime('%Y-%m-%d %H:%M')}.\n\n"
    message += f"Description: {task.description}\n"
    message += f"Priority: {task.priority.upper()}"
    
    if user.notification_preference in ['email', 'both']:
        send_email_notification(user.email, subject, message)
    
    if user.notification_preference in ['sms', 'both'] and user.phone_number:
        send_sms_notification(user.phone_number, f"TASKMASTER: '{task.title}' due on {task.deadline.strftime('%m/%d %H:%M')}")