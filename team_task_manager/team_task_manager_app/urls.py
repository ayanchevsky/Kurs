from django.urls import path
from team_task_manager_app.views import *

urlpatterns = [
    path('tasks/<pk>/', OneTask.as_view()),
    path('tasks/', Tasks.as_view()),
]
