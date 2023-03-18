import pytest as pytest
from rest_framework.test import APIClient
from model_bakery import baker

from team_task_manager_app.models import Task, User


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def count():
    return Task.objects.count()


@pytest.fixture
def task_factory():
    def factory(*args, **kwargs):
        return baker.make(Task, *args, **kwargs)
    return factory


@pytest.fixture
def user_factory():
    def factory(*args, **kwargs):
        return baker.make(User, *args, **kwargs)
    return factory


@pytest.mark.django_db
def test_task(client, task_factory):
    tasks = task_factory()
    responce = client.get(f'/api/tasks/{tasks.id}/')
    data = responce.json()
    assert responce.status_code == 200
    assert tasks.title == data['title']


# проверка получения списка задач (list-логика)
@pytest.mark.django_db
def test_courses(client, task_factory):
    tasks = task_factory(_quantity=10)
    responce = client.get('/api/tasks/')
    assert responce.status_code == 200
    data = responce.json()
    for i, course in enumerate(data):
        assert course['title'] == tasks[i].title

# проверка фильтрации списка задач по id
@pytest.mark.django_db
def test_id(client, task_factory):
    tasks = task_factory(_quantity=10)
    tasks_id = tasks[5].id
    responce = client.get(f'/api/tasks/?id={tasks_id}')
    assert responce.status_code == 200
    data = responce.json()
    assert data[0]['id'] == tasks_id


# проверка фильтрации списка курсов по name
@pytest.mark.django_db
def test_name(client, task_factory):
    tasks = task_factory(_quantity=10)
    tasks_name = tasks[5].title
    responce = client.get(f'/api/tasks/?name={tasks_name}')
    assert responce.status_code == 200
    data = responce.json()
    assert data[0]['name'] == tasks_name


# тест успешного создания задачи
@pytest.mark.django_db
def test_create(client, task_factory, count):
    tasks = task_factory()
    responce = client.get(f'/api/tasks/?name={tasks.title}')
    assert responce.status_code == 200
    assert Task.objects.count() == count + 1


# тест успешного обновления задачи
@pytest.mark.django_db
def test_update(client, task_factory):
    tasks = task_factory()
    responce = client.patch(f'/api/tasks/{tasks.id}/', data={'title': 'Test2'}, format='json')
    data_new = responce.json()
    assert responce.status_code == 200
    assert tasks.title != data_new["title"]


# тест успешного удаления задачи
@pytest.mark.django_db
def test_delete(client, task_factory, count):
    tasks = task_factory()
    assert Task.objects.count() == count + 1
    responce = client.delete(f'/api/tasks/{tasks.id}/')
    assert responce.status_code == 204
    assert Task.objects.count() == count
