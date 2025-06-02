from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    notification_preference = models.CharField(
        max_length=10, 
        choices=[('email', 'Email'), ('sms', 'SMS'), ('both', 'Both')],
        default='email'
    )