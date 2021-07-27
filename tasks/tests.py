from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from tasks.logger import logger
from tasks.models import Label, MyUser, Status, Task

logger.info('Running tests for task app')


class TasksUserViewsTests(TestCase):
    """Test views for user."""

    fixtures = ['data.json']

    def setUp(self):
        self.reg_info = {
            'first_name': 'test3',
            'last_name': 'test3',
            'username': 'test3',
            'password1': 'xcCC_123f5',
            'password2': 'xcCC_123f5',
        }
        self.credentials = {
            'username': 'test1',
            'password': 'http://localhost:8000/',
        }
        self.upd_credentials = {
            'username': 'KwaKwa',
            'password': 'levox3fgv',
        }

    def test_index(self):
        url = reverse('tasks:index')
        response = self.client.get(url)  # noqa: WPS204 Overused expression
        self.assertEqual(response.status_code, 200)

    def test_list(self):
        url = reverse('tasks:user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_registration(self):
        reg_info = self.reg_info
        url = reverse('tasks:user-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        users = get_user_model().objects.all()
        self.client.post(url, reg_info)
        self.assertEqual(users.get(username='test3').username, 'test3')
        self.assertEqual(users.count(), 4)  # 3 + 1

    def test_login(self):
        url = reverse('tasks:user-login')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        credentials = self.credentials
        login = self.client.post(url, credentials)
        self.assertEqual(login.status_code, 302)

    def test_delete_update(self):
        url_update = reverse('tasks:user-update', kwargs={'pk': 3})
        url_delete = reverse('tasks:user-delete', kwargs={'pk': 3})
        response_upd = self.client.get(url_update)
        response_del = self.client.get(url_delete)
        self.assertEqual(response_del.status_code, 302)
        self.assertEqual(response_upd.status_code, 302)

        # Update and delete for test1 with pk=77 after login.
        self.client.post(reverse('tasks:user-login'), self.credentials)
        response_upd = self.client.post(
            url_update,
            {'first_name': 'Ivan', 'last_name': 'Ivanov', 'username': 'KwaKwa', 'password1': 'levox3fgv', 'password2': 'levox3fgv'},  # noqa: E501
        )
        users = get_user_model().objects.all()
        self.assertEqual(users.get(pk=3).username, 'KwaKwa')

        self.client.post(reverse('tasks:user-login'), self.upd_credentials)
        response_del = self.client.post(url_delete, kwargs={'pk': 3})
        users = get_user_model().objects.all()
        with self.assertRaises(MyUser.DoesNotExist):
            users.get(pk=3)


class TasksStatusViewsTests(TestCase):
    """Test status views."""

    fixtures = ['data.json']

    def setUp(self):
        self.credentials = {
            'username': 'test1',
            'password': 'http://localhost:8000/',
        }
        self.login = self.client.post(
            reverse('tasks:user-login'),
            self.credentials,
        )

    def test_list(self):
        url = reverse('tasks:status-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create(self):
        url = reverse('tasks:status-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.client.post(url, {'name': 'In Review'})
        self.assertEqual(Status.objects.all().count(), 5)  # 4 + 1
        self.assertEqual(Status.objects.get(pk=2).id, 2)

    def test_update(self):
        url = reverse('tasks:status-update', kwargs={'pk': 3})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.client.post(url, {'name': 'Big DEAL'})
        self.assertEqual(Status.objects.get(pk=3).name, 'Big DEAL')

    def test_delete(self):
        url = reverse('tasks:status-delete', kwargs={'pk': 3})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.client.post(url)
        with self.assertRaises(Status.DoesNotExist):
            Status.objects.get(pk=3)


class TasksViewsTests(TestCase):
    """Test status views."""

    fixtures = ['data.json']

    def setUp(self):
        self.credentials = {
            'username': 'test1',
            'password': 'http://localhost:8000/',
        }
        self.login = self.client.post(
            reverse('tasks:user-login'),
            self.credentials,
        )

        self.task = {
            'name': 'test task',
            'description': 'smth',
            'status': 3,
            'executor': 2,
        }

    def test_single(self):
        url = reverse('tasks:task', kwargs={'pk': 3})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_list(self):
        url = reverse('tasks:task-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create(self):
        url = reverse('tasks:task-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.client.post(url, self.task)
        self.assertEqual(Task.objects.all().count(), 4)  # 3 + 1
        self.assertEqual(Task.objects.get(name='test task').id, 5)

    def test_update(self):
        url = reverse('tasks:task-update', kwargs={'pk': 4})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.client.post(url, self.task)
        self.assertEqual(Task.objects.get(pk=4).name, 'test task')

    def test_delete(self):
        url = reverse('tasks:task-delete', kwargs={'pk': 4})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.client.post(url)
        with self.assertRaises(Task.DoesNotExist):
            Task.objects.get(pk=4)


class TasksLabelTests(TestCase):
    """Test status views."""

    fixtures = ['data.json']

    def setUp(self):
        self.credentials = {
            'username': 'test1',
            'password': 'http://localhost:8000/',
        }
        self.login = self.client.post(
            reverse('tasks:user-login'),
            self.credentials,
        )

        self.label = {
            'name': 'My label',
        }

    def test_list(self):
        url = reverse('tasks:label-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create(self):
        url = reverse('tasks:label-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.client.post(url, self.label)
        self.assertEqual(Label.objects.all().count(), 5)  # 4 + 1
        self.assertEqual(Label.objects.get(name='My label').id, 5)

    def test_update(self):
        url = reverse('tasks:label-update', kwargs={'pk': 2})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.client.post(url, self.label)
        self.assertEqual(Label.objects.get(pk=2).name, 'My label')

    def test_delete(self):
        url = reverse('tasks:label-delete', kwargs={'pk': 2})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        Label.objects.get(pk=2)

        url = reverse('tasks:label-delete', kwargs={'pk': 4})
        self.client.post(url)
        with self.assertRaises(Label.DoesNotExist):
            Label.objects.get(pk=4)
