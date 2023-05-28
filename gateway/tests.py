from django.conf import settings
from django.test import TestCase, Client

from gateway.models import Contest, User, Subscribe, Command
from rest_framework.test import APIClient
import random
from django.utils import timezone
from datetime import timedelta, datetime

from .forms import SendSolutionValidationForm
from .models import Contest, Tag
from .serializers import ContestCreateSerializer, CommandCreateSerializer
from .utils import create_test_contest, create_test_contest_json, create_test_subscribe, create_test_command_json, \
    create_test_command, create_test_task

from django.utils.timezone import activate
activate(settings.TIME_ZONE)

class ListContestAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.contest1 = create_test_contest(10, self.user)
        self.contest2 = create_test_contest(10, self.user)
        self.contest3 = create_test_contest(10, self.user)

    def test_contest_list(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/contest/list/', format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)


class CreateContestAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_create_contest(self):
        self.client.login(username='testuser', password='testpassword')
        data = create_test_contest_json(10)
        data["owner"] = self.user.id
        response = self.client.post('/contest/create/', data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Contest.objects.count(), 1)
        self.assertEqual(Contest.objects.get().name, data.get("name"))


class UpdateContestAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.contest = create_test_contest(10, self.user)

    def test_update_contest(self):
        self.client.login(username='testuser', password='testpassword')

        new_data = ContestCreateSerializer(self.contest).data
        new_data["name"] = "new Name"
        response = self.client.put(f'/contest/update/{self.contest.id}/', new_data, format='json')

        self.assertEqual(response.status_code, 200)
        self.contest.refresh_from_db()
        self.assertEqual(self.contest.name, new_data.get("name"))


class ListSubscribeAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        # предполагается, что у пользователя есть подписки
        self.subscribe1 = create_test_subscribe()
        self.subscribe2 = create_test_subscribe()

    def test_list_subscribe(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/rate/all/', format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)


class ListMySubscribeAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        # предполагается, что у пользователя есть подписки
        self.subscribe1 = create_test_subscribe()
        self.subscribe2 = create_test_subscribe()
        self.user.subscribe = self.subscribe2
        self.user.save()

    def test_list_my_subscribe(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/rate/my/', format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)


class CreateCommandAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.contest = create_test_contest(10, self.user)

    def test_create_command(self):
        self.client.login(username='testuser', password='testpassword')
        data = create_test_command_json()
        data["admin"] = self.user.id
        data["contest"] = self.contest.id
        response = self.client.post('/command/create/', data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Command.objects.count(), 1)
        self.assertEqual(Command.objects.get().command_name, data.get("command_name"))


class UpdateCommandAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.contest = create_test_contest(10, self.user)
        self.command = create_test_command(contest=self.contest, admin=self.user)

    def test_update_command(self):
        self.client.login(username='testuser', password='testpassword')

        new_data = CommandCreateSerializer(self.command).data
        new_data["command_name"] = "new Name"
        response = self.client.put(f'/command/update/{self.command.id}/', new_data, format='json')

        self.assertEqual(response.status_code, 200)
        self.command.refresh_from_db()
        self.assertEqual(self.command.command_name, new_data.get("command_name"))


class ListCommandAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser1', password='testpassword')
        self.user2 = User.objects.create_user(username='testuser2', password='testpassword')
        self.user3 = User.objects.create_user(username='testuser3', password='testpassword')

        self.contest = create_test_contest(10, self.user)
        self.command1 = create_test_command(contest=self.contest, admin=self.user)
        self.command2 = create_test_command(contest=self.contest, admin=self.user2)
        self.command3 = create_test_command(contest=self.contest, admin=self.user3)

    def test_command_list(self):
        self.client.login(username='testuser1', password='testpassword')
        response = self.client.get('/command/list/', format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)


class GetCommandAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.contest = create_test_contest(10, self.user)
        self.command = create_test_command(contest=self.contest, admin=self.user)

    def test_get_command(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(f'/command/get/{self.command.id}', format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['command_name'], self.command.command_name)


class CreateMultipleCommandAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.contest = create_test_contest(10, self.user)

    def test_create_multiple_command(self):
        self.client.login(username='testuser', password='testpassword')

        data = create_test_command_json()
        data["admin"] = self.user.id
        data["contest"] = self.contest.id

        # First command should be created successfully
        response = self.client.post('/command/create/', data, format='json')
        # print(response.data)
        self.assertEqual(response.status_code, 201)

        # Second command should fail
        response = self.client.post('/command/create/', data, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertIn('You can only once create a command', str(response.data['detail']))


class UpdateCommandPermissionAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_user(username='testadmin', password='testpassword')
        self.non_admin_user = User.objects.create_user(username='testuser', password='testpassword')
        self.contest = create_test_contest(10, self.admin_user)
        self.command = create_test_command(contest=self.contest, admin=self.admin_user)

    def test_update_command_non_admin(self):
        self.client.login(username='testuser', password='testpassword')

        new_data = CommandCreateSerializer(self.command).data
        new_data["command_name"] = "new Name"

        response = self.client.put(f'/command/update/{self.command.id}/', new_data, format='json')
        self.assertEqual(response.status_code, 403)


class CreateCommandAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.contest = create_test_contest(10, self.user)
        self.start_time = timezone.now() + timedelta(hours=1)
        self.end_time = timezone.now() + timedelta(hours=2)
        self.contest.reg_start = self.start_time
        self.contest.reg_end = self.end_time
        self.contest.save()

    def test_create_command_wrong_time(self):
        self.client.login(username='testuser', password='testpassword')
        data = create_test_command_json()
        data["admin"] = self.user.id
        data["contest"] = self.contest.id
        response = self.client.post('/command/create/', data, format='json')

        self.assertEqual(response.status_code, 403)
        self.assertIn('The request should be made between reg_start and reg_end of the contest', str(response.data['detail']))


class SendSolutionTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.contest = create_test_contest(10, self.user)
        self.command = create_test_command(contest=self.contest, admin=self.user)
        self.solution_data = {
                "solution_url": "1234@example.com",
                "command_id": self.command.id
                }

    def test_send_solution_validation(self):
        self.client.login(username='testuser', password='testpassword')
        # Add your specific solution data here

        form = SendSolutionValidationForm(self.solution_data)

        self.assertEqual(form.is_valid(), True)

    def test_send_not_valid_solution(self):
        self.client.login(username='testuser', password='testpassword')
        # Add your specific solution data here
        self.solution_data['solution_url'] = "1234"
        response = self.client.post('/solution/send', self.solution_data, format='json')
        self.solution_data['solution_url'] = "1234@example.com"

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['solution_url'][0], 'Enter a valid URL.')

    def test_send_bad_solution(self):
        self.client.login(username='testuser', password='testpassword')
        # Add your specific solution data here

        response = self.client.post('/solution/send', self.solution_data, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertIn('You must send a correct github repository url', response.data['detail'])

    # def test_send_solution_within_contest_duration(self):
    #     self.solution_data = {
    #         "solution_url": "https://github.com/sudovag3/ThreadsProg",
    #         "command_id": self.command.id
    #     }
    #     self.client.login(username='testuser', password='testpassword')
    #     self.contest = create_test_contest(10, self.user)
    #     self.contest.date_start = datetime(2023, 5, 5, 5, 49, 0)
    #     self.contest.date_end = datetime(2023, 5, 5, 7, 0, 0)
    #     self.contest.save()
    #
    #     response = self.client.post('/solution/send', self.solution_data, format='json')
    #     self.assertEqual(response.status_code, 200)
    #     # Добавьте здесь дополнительные проверки в зависимости от вашего API

    def test_send_solution_after_contest_duration(self):
        self.solution_data = {
            "solution_url": "https://github.com/sudovag3/ThreadsProg",
            "command_id": self.command.id
        }
        self.client.login(username='testuser', password='testpassword')
        self.contest.date_start = datetime(2023, 5, 5, 3, 0, 0)
        self.contest.date_end = datetime(2023, 5, 5, 14, 0, 0)
        self.contest.save()

        response = self.client.post('/solution/send', self.solution_data, format='json')
        self.assertEqual(response.status_code, 403)
        # print(response.data['detail'])
        self.assertEqual(response.data['detail'], 'You can send solution in right commit date range')

    def test_send_solution_correct(self):
        self.solution_data = {
            "solution_url": "https://github.com/sudovag3/ThreadsProg",
            "command_id": self.command.id
        }
        self.command.task = create_test_task()
        self.command.save()
        self.client.login(username='testuser', password='testpassword')
        self.contest.date_start = datetime(2023, 5, 5, 3, 0, 0)
        self.contest.date_end = datetime(2023, 5, 5, 17, 0, 0)
        self.contest.save()

        response = self.client.post('/solution/send', self.solution_data, format='json')
        # print(response.data)
        self.assertEqual(response.status_code, 200)

