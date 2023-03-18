import datetime
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.permissions import IsAuthenticated, BasePermission
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import TaskForm
from .models import Task, Logging
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .serializers import *


class OnlyOwnerPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == "DELETE":
            return obj.creator_id == request.user.id
        elif request.method in ["GET", "POST", "PATCH", "PUT"]:
            return request.user.id in obj.assigned_user_id
        return False


def home(request):
    return render(request, 'home.html')


def signupuser(request):
    if request.method == 'GET':
        return render(request, 'signupuser.html', {'form':UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('currenttasks')
            except IntegrityError:
                return render(request, 'signupuser.html',
                              {'form':UserCreationForm(),
                               'error': 'That username has already been taken. Please choose a new username'})
        else:
            return render(request, 'signupuser.html',
                          {'form': UserCreationForm(),
                           'error': 'Passwords did not match'})

def loginuser(request):
    if request.method == 'GET':
        return render(request,
                      'loginuser.html',
                      {'form': AuthenticationForm()})
    else:
        user = authenticate(request,
                            username=request.POST['username'],
                            password=request.POST['password'])
        if user is None:
            return render(request, 'loginuser.html',
                          {'form': AuthenticationForm(),
                           'error': 'Username and password did not match'})
        else:
            login(request, user)
            return redirect('currenttasks')


@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')


@login_required
def createtask(request):
    context = {
        'this_user': User.objects.get(id=request.user.id),
        'users': User.objects.all(),
        'form': TaskForm()
    }
    if request.method == 'GET':
        return render(request, 'createtask.html', context)
    else:
        try:
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)
            new_task.creator = request.user
            new_task.save()
            assigned_user = User.objects.get(id=request.POST['assigned_user'])
            new_task.assigned_user.add(assigned_user.id)
            new_task.save()
            log = Logging(task=new_task, action='CREATE', modifier=request.user)
            log.save()
            return redirect('currenttasks')
        except ValueError as ex:
            print(ex)
            context.update({'error': 'Bad data passed in. Try again.'})
            return render(request, 'createtask.html', context)


@login_required
def currenttasks(request):
    todos = Task.objects.filter(Q(creator_id=request.user.id, date_completed__isnull=True) |
                                Q(assigned_user=request.user.id, date_completed__isnull=True)).distinct()
    return render(request, 'currenttask.html', {'todos': todos})


@login_required
def completedtasks(request):
    todos = Task.objects.filter(Q(creator_id=request.user.id, date_completed__isnull=False) |
                                Q(assigned_user=request.user.id, date_completed__isnull=False)).distinct()
    return render(request, 'completedtask.html', {'todos': todos})


@login_required
def viewtask(request, todo_pk):
    todo = get_object_or_404(Task, id=todo_pk)
    if request.method == 'GET':
        form = TaskForm(instance=todo)
        task = get_object_or_404(Task, id=todo_pk)
        assigned_user = task.assigned_user
        context = {
            'users': User.objects.all(),
            'this_user': User.objects.get(id=request.user.id),
            'task': task,
            'assigned_user': [user for user in assigned_user.all()],
            'due_date': task.due_date,
            'date_completed': todo.date_completed,
            'completion_notes': todo.completion_notes,
            'todo': todo,
            'form': form

        }
        return render(request, 'viewtask.html', context)        # {'todo': todo, 'form': form})
    else:
        try:
            form = TaskForm(request.POST, instance=todo)
            new_task = form.save(commit=False)
            new_task.creator = request.user
            new_task.save()
            assigned_user = User.objects.get(id=request.POST['assigned_user'])
            new_task.assigned_user.add(assigned_user.id)
            new_task.save()
            log = Logging(task=new_task, action='UPDATE', modifier=request.user)
            log.save()
            return redirect('currenttasks')
        except ValueError as ex:
            return render(request, 'viewtask.html', {'todo': todo, 'form': form, 'error': 'Bad info'})


@login_required
def completetask(request, todo_pk):
    task = get_object_or_404(Task, id=todo_pk)
    assigned_user = task.assigned_user
    context = {
        'users': User.objects.all(),
        'this_user': User.objects.get(id=request.user.id),
        'task': task,
        'assigned_user': [user for user in assigned_user.all()],
        'due_date': task.due_date,
        'close_date': datetime.datetime.now(),
    }
    return render(request, 'complete_task.html', context)


@login_required
def task_completion(request, todo_pk):
    todo = get_object_or_404(Task, id=todo_pk)
    if request.method == 'POST':
        todo.completion_notes = request.POST['completion_notes']
        todo.date_completed = datetime.datetime.now()
        todo.save()
        log = Logging(task=todo, action='CLOSE', modifier=request.user)
        log.save()
    return redirect('currenttasks')


@login_required
def deletetask(request, todo_pk):
    todo = Task.objects.filter(id=todo_pk, creator=request.user.id)
    if request.method == 'POST':
        todo.delete()
        return redirect('currenttasks')


@login_required
def taskstart(request, todo_pk):
    todo = get_object_or_404(Task, id=todo_pk, creator=request.user.id)
    if request.method == 'POST':
        todo.completion_notes = None
        todo.date_completed = None
        todo.save()
        log = Logging(task=todo, action='START')
        log.save()
        log.modifier.add(request.user)
        log.save()
        return redirect('currenttasks')


@login_required
def history(request, todo_pk):
    history = Logging.objects.filter(task_id=todo_pk)
    if request.method == 'POST':
        context = {
            'history': history,
        }
        return render(request, 'history.html', context)


class Tasks(ListAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def post(self, request):
        title = request.data.get('title', None)
        description = request.data.get('description', None)
        due_date = request.data.get('due_date', None)
        user = request.data.get('assigned_user', None)
        assigned_user = get_object_or_404(User, username=user)

        if title and description and due_date and assigned_user:
            Task(title=title, description=description,
                 due_date=due_date,
                 assigned_user=assigned_user,
                 user=request.user).save()
            return Response({'Create': 'Success'})
        else:
            return Response({'Create': 'Failed'})


class OneTask(APIView):
    filter_backends = [DjangoFilterBackend]

    def get_object(self, pk):
        return Task.objects.get(id=pk)

    def get(self, request, pk):
        obj = self.get_object(pk)
        ser = TaskDetailSerializer(obj)
        return Response(ser.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        obj = self.get_object(pk)
        ser = TaskSerializer(obj, data=request.data, partial=True)
        if ser.is_valid():
            ser.save()
            return Response(ser.data, status=status.HTTP_201_CREATED)
        else:
            Response(ser.data, status=status.HTTP_400_BAD_REQUEST)

