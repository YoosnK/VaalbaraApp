from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from ivm.models import Transaction

User = get_user_model()

class Task(models.Model):
    title = models.CharField(max_length=100)
    body = models.TextField()
    creation_date = models.DateTimeField(default=timezone.now)
    completion_deadline = models.DateTimeField(null=True, blank=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="tasks_given")
    task_for = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tasks")
    is_complete = models.BooleanField(default=False)

    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, null=True, blank=True, related_name="tasks")

    @property
    def is_overdue(self):
        return timezone.now() > self.completion_deadline
    
    def __str__(self):
        return self.title