from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields.related import ManyToManyField


class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateTimeField(null=True)
    creator = models.ForeignKey(User, related_name="has_created_task", on_delete=models.CASCADE)
    assigned_user = ManyToManyField(User, related_name="users_tasks")
    completion_notes = models.TextField(null=True)
    date_completed = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Logging(models.Model):
    task = models.ForeignKey(Task, related_name="task_log", on_delete=models.CASCADE)
    modifier = models.ForeignKey(User, related_name="modifier_task", on_delete=models.CASCADE)
    action = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)
