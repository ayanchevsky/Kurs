"""team_task_manager URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from team_task_manager_app import views
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth
    path('signup/', views.signupuser, name='signupuser'),
    path('login/', views.loginuser, name='loginuser'),
    path('logout/', views.logoutuser, name='logoutuser'),

    # Tasks
    path('', views.home, name='home'),
    path('create/', views.createtask, name='createtask'),
    path('current/', views.currenttasks, name='currenttasks'),
    path('completed/', views.completedtasks, name='completedtasks'),
    path('todo/<int:todo_pk>', views.viewtask, name='viewtask'),
    path('todo/<int:todo_pk>/complete', views.completetask, name='completedtask'),
    path('todo/<int:todo_pk>/delete', views.deletetask, name='deletetask'),
    path('task_completion/<int:todo_pk>', views.task_completion, name='taskcompletion'),
    path('taskstart/<int:todo_pk>', views.taskstart, name='taskstart'),
    path('todo/<int:todo_pk>/history', views.history, name='history'),
    # API
    path('api/', include('team_task_manager_app.urls')),
]
