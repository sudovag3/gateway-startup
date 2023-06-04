from django.conf import settings
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status

from gateway.models import Contest, User, Subscribe, Command, Review, Award, Task, Invite
from rest_framework.test import APIClient, APITestCase
import random
from django.utils import timezone
from datetime import timedelta, datetime

from .forms import SendSolutionValidationForm
from .models import Contest, Tag
from .serializers import ContestCreateSerializer, CommandCreateSerializer
from .utils import create_test_contest, create_test_contest_json, create_test_subscribe, create_test_command_json, \
    create_test_command, create_test_task, create_test_award

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


class TestSetParticipantAPIView(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.contest = create_test_contest(10, self.user)
        self.contest.reg_start = timezone.now()
        self.contest.reg_end = timezone.now() + timedelta(days=1)
        self.contest.save()
        self.client = APIClient()

    def test_user_registers_to_contest(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(
            '/contest/set_participant/',
            {'contest_id': self.contest.id},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.contest.refresh_from_db()
        self.assertIn(self.user, self.contest.participants.all())

    def test_user_registers_twice_to_contest(self):
        self.client.login(username='testuser', password='testpassword')
        self.client.post(
            '/contest/set_participant/',
            {'contest_id': self.contest.id},
            format='json'
        )

        response = self.client.post(
            '/contest/set_participant/',
            {'contest_id': self.contest.id},
            format='json'
        )


        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.contest.refresh_from_db()
        self.assertEqual(self.contest.participants.count(), 1)

    def test_user_registers_outside_reg_time(self):
        self.contest.reg_start = timezone.now() - timedelta(days=2)
        self.contest.reg_end = timezone.now() - timedelta(days=1)
        self.contest.save()

        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(
            '/contest/set_participant/',
            {'contest_id': self.contest.id},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'The request should be made between reg_start and reg_end of the contest')


class TestSetContestAdminAPIView(APITestCase):

    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='password')
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.contest = create_test_contest(10, self.owner)
        self.client = APIClient()

    def test_non_owner_tries_to_set_admin(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(
            '/contest/set_admin/',
            {'contest_id': self.contest.id, 'participant_id': self.user.id},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'You can only set admins to contest owned to you.')

    def test_owner_tries_to_set_admin_with_invalid_form(self):
        self.client.login(username='owner', password='password')
        response = self.client.post(
            '/contest/set_admin/',
            {'contest_id': self.contest.id},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_sets_wrong_user(self):
        self.client.login(username='owner', password='password')
        response = self.client.post(
            '/contest/set_admin/',
            {'contest_id': self.contest.id, 'participant_id': 123},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], f'Not valid user - {123}')

    def test_owner_sets_wrong_user(self):
        self.client.login(username='owner', password='password')
        response = self.client.post(
            '/contest/set_admin/',
            {'contest_id': self.contest.id, 'participant_id': self.user.id},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], f'User {self.user.id} not register')


    def test_owner_sets_admin(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.post(
            '/contest/set_participant/',
            {'contest_id': self.contest.id},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.login(username='owner', password='password')
        response = self.client.post(
            '/contest/set_admin/',
            {'contest_id': self.contest.id, 'participant_id': self.user.id},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.contest.refresh_from_db()
        self.assertIn(self.user, self.contest.contest_admins.all())


class TestCreateReviewAPIView(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='password')
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.contest = create_test_contest(10, self.owner)
        self.command = create_test_command(contest=self.contest, admin=self.user)
        self.client = APIClient()

    def test_create_review_successfully(self):
        self.client.login(username='owner', password='password')
        response = self.client.post(
            '/review/send/',
            {'command': self.command.id, 'reviewer': self.owner.id, 'mark': 10, 'comment': 'Good'},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.get().mark, 10)

    def test_create_second_review_for_the_same_command(self):
        self.client.login(username='owner', password='password')
        self.client.post(
            '/review/send/',
            {'command': self.command.id, 'reviewer': self.owner.id, 'mark': 10, 'comment': 'Good'},
            format='json'
        )

        response = self.client.post(
            '/review/send/',
            {'command': self.command.id, 'reviewer': self.owner.id, 'mark': 5, 'comment': 'Good'},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'Not valid Review')

    def test_create_review_by_non_owner(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(
            '/review/send/',
            {'command': self.command.id, 'reviewer': self.user.id, 'mark': 10, 'comment': 'Good'},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'Not Owner/Admin')


    def test_create_review_with_wrong_reviewer(self):
        self.client.login(username='owner', password='password')
        response = self.client.post(
            '/review/send/',
            {'command': self.command.id, 'reviewer': 123, 'mark': 10, 'comment': 'Good'},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'Wrong reviewer')

# Award
class TestAwardView(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.contest = create_test_contest(10, self.user)
        self.task = create_test_task(self.contest)
        self.command = create_test_command(self.contest, self.user)
        self.award = create_test_award(self.command, self.task)
        self.client = APIClient()

    def test_create_award_successfully(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(
            '/award/create/',
            {'task': self.task.id, 'command': self.command.id, 'name': "Best"},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(Award.objects.get(task=self.task, command=self.command, name="Best"))

    def test_create_award_unauthenticated(self):
        response = self.client.post(
            '/award/create/',
            {'task': self.task.id, 'command': self.command.id},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_award_with_invalid_task(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(
            '/award/create/',
            {'task': 999, 'command': self.command.id},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_award_with_invalid_command(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(
            '/award/create/',
            {'task': self.task.id, 'command': 999},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Tests for Award update

    def test_update_award_successfully(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.put(
            f'/award/{self.award.id}/update/',
            {'task': self.task.id, 'command': self.command.id, 'name': 'Better Task', 'description': 'For the better task', 'award': 'Silver Medal'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.award.refresh_from_db()
        self.assertEqual(self.award.name, 'Better Task')
        self.assertEqual(self.award.description, 'For the better task')
        self.assertEqual(self.award.award, 'Silver Medal')

    def test_update_award_unauthenticated(self):
        response = self.client.put(
            f'/award/{self.award.id}/update/',
            {'task': self.task.id, 'command': self.command.id, 'name': 'Better Task', 'description': 'For the better task', 'award': 'Silver Medal'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_award_non_existent(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.put(
            '/award/999/update/',
            {'task': self.task.id, 'command': self.command.id, 'name': 'Better Task', 'description': 'For the better task', 'award': 'Silver Medal'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Tests for Award deletion

    def test_delete_award_successfully(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.delete(
            f'/award/{self.award.id}/delete/',
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Award.DoesNotExist):
            Award.objects.get(id=self.award.id)

    def test_delete_award_unauthenticated(self):
        response = self.client.delete(
            f'/award/{self.award.id}/delete/',
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_award_non_existent(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.delete(
            '/award/999/delete/',
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Tests for listing Awards

    def test_list_awards_successfully(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(
            '/award/list/',
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.award.id)

    def test_list_awards_unauthenticated(self):
        response = self.client.get(
            '/award/list/',
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

# Task
class TestTaskView(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.contest = create_test_contest(10, self.user)
        self.tag = Tag.objects.create(name="Test tag")
        self.client = APIClient()

    def test_create_task_successfully(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(
            '/task/create/',
            {'task_name': 'Test task', 'task_description': 'Test description', 'contest': self.contest.id, 'tags': [self.tag.id]},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(Task.objects.get(task_name='Test task'))

    def test_create_task_unauthenticated(self):
        response = self.client.post(
            '/task/create/',
            {'name': 'Test task', 'description': 'Test description', 'contest': self.contest.id, 'tags': [self.tag.id]},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_task_with_invalid_contest(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(
            '/task/create/',
            {'name': 'Test task', 'description': 'Test description', 'contest': 999, 'tags': [self.tag.id]},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_task_with_invalid_tag(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(
            '/task/create/',
            {'name': 'Test task', 'description': 'Test description', 'contest': self.contest.id, 'tags': [999]},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_update_task_successfully(self):
        self.client.login(username='testuser', password='testpassword')
        task = Task.objects.create(task_name='Old task', contest=self.contest)
        response = self.client.put(
            f'/task/{task.id}/update/',
            {'task_name': 'Updated task', 'task_description': 'Updated description', 'contest': self.contest.id, 'tags': [self.tag.id]},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Task.objects.get(id=task.id).task_name, 'Updated task')

    def test_update_task_unauthenticated(self):
        task = Task.objects.create(task_name='Old task', contest=self.contest)
        response = self.client.put(
            f'/task/{task.id}/update/',
            {'task_name': 'Updated task', 'task_description': 'Updated description', 'contest': self.contest.id, 'tags': [self.tag.id]},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_task_successfully(self):
        self.client.login(username='testuser', password='testpassword')
        task = Task.objects.create(task_name='Task to delete', contest=self.contest)
        response = self.client.delete(
            f'/task/{task.id}/delete/',
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Task.DoesNotExist):
            Task.objects.get(id=task.id)

    def test_list_tasks_successfully(self):
        self.client.login(username='testuser', password='testpassword')
        Task.objects.create(task_name='Task 1', contest=self.contest)
        Task.objects.create(task_name='Task 2', contest=self.contest)
        response = self.client.get(
            '/task/list/',
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

# Invite
class TestInviteViews(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.user1 = User.objects.create_user(username='user1', password='pass')
        self.user2 = User.objects.create_user(username='user2', password='pass')
        self.contest = create_test_contest(10, self.user)
        self.command = create_test_command(self.contest, self.user1)
        # self.command.participants.add(self.user2)
        # self.command.save()
        self.client = APIClient()

    def test_create_invite_successfully(self):
        self.client.login(username='user2', password='pass')
        response = self.client.post(reverse('create_invite'), {'command': self.command.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Invite.objects.filter(invited=self.user2, command=self.command).exists())

    def test_send_invite_successfully(self):
        self.client.login(username='user1', password='pass')
        response = self.client.post(reverse('send_invite'), {'command': self.command.id, 'invited': self.user2.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Invite.objects.filter(invited=self.user2, command=self.command).exists())

    def test_list_invites_successfully(self):
        self.client.login(username='user2', password='pass')
        Invite.objects.create(command=self.command, inviter=self.user1, invited=self.user2, status=Invite.Status.CREATED)
        response = self.client.get(reverse('list_invite'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_applications_successfully(self):
        self.client.login(username='user1', password='pass')
        Invite.objects.create(command=self.command, inviter=self.user1, invited=self.user2, status=Invite.Status.CREATED)
        response = self.client.get(reverse('list_application'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_accept_application_successfully(self):
        self.client.login(username='user1', password='pass')
        invite = Invite.objects.create(command=self.command, inviter=self.user1, invited=self.user2,
                                       status=Invite.Status.CREATED)
        response = self.client.post(reverse('accept_decline_application'), {'invite': invite.id, 'accept': True},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        invite.refresh_from_db()
        self.assertEqual(invite.status, Invite.Status.ACCEPTED)

    def test_decline_application_successfully(self):
        self.client.login(username='user1', password='pass')
        invite = Invite.objects.create(command=self.command, inviter=self.user1, invited=self.user2,
                                       status=Invite.Status.CREATED)
        response = self.client.post(reverse('accept_decline_application'), {'invite': invite.id, 'accept': False},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        invite.refresh_from_db()
        self.assertEqual(invite.status, Invite.Status.REJECTED)

    def test_accept_invite_successfully(self):
        self.client.login(username='user2', password='pass')
        invite = Invite.objects.create(command=self.command, inviter=self.user1, invited=self.user2,
                                       status=Invite.Status.CREATED)
        response = self.client.post(reverse('accept_decline_invite'), {'invite': invite.id, 'accept': True},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        invite.refresh_from_db()
        self.assertEqual(invite.status, Invite.Status.ACCEPTED)

    def test_decline_invite_successfully(self):
        self.client.login(username='user2', password='pass')
        invite = Invite.objects.create(command=self.command, inviter=self.user1, invited=self.user2,
                                       status=Invite.Status.CREATED)
        response = self.client.post(reverse('accept_decline_invite'), {'invite': invite.id, 'accept': False},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        invite.refresh_from_db()
        self.assertEqual(invite.status, Invite.Status.REJECTED)


