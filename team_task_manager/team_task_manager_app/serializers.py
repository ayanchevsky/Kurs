from rest_framework import serializers
from .models import Task


# class MeasurementSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Task
#         fields = ['created_at', 'creator']


class TaskDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = ['id', 'created_at', 'creator', 'title', 'description', 'due_date', 'assigned_user', 'completion_notes', 'date_completed']


class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = ['id', 'created_at', 'creator', 'title', 'description', 'due_date', 'assigned_user']


