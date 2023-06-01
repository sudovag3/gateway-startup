
from gateway.enums.user_contest_type import UserContestType
from gateway.models import Contest, User, Command, Task, Award, Subscribe, Solution
import random
from django.utils import timezone
from datetime import timedelta
from .models import Contest, Tag


def type_of_user_contest(user, id) -> UserContestType:
    if Contest.objects.filter(id = id, contest_admins__id=user.id).exists() or Contest.objects.filter(id= id, owner__id=user.id).exists():
        return UserContestType.admin
    elif Contest.objects.filter(id= id, participants__id=user.id).exists():
        return UserContestType.participant
    else:
        return UserContestType.guest

def create_test_contest(name_length=10, owner = "", participants = 0):
    """
    Создает тестовый объект Contest со случайными значениями.
    """
    name = generate_random_string(name_length)
    status = random.choice([choice[0] for choice in Contest.Status.choices])
    description = generate_random_string(100)
    reg_start = timezone.now()
    reg_end = timezone.now() + timedelta(days=10)
    date_start = reg_end + timedelta(days=5)
    date_end = date_start + timedelta(days=5)
    logo = generate_random_string(10)
    participant_cap = random.randint(1, 100)
    command_min = random.randint(1, 10)
    command_max = random.randint(command_min, 20)
    region = generate_random_string(10)
    owner = owner if owner else create_test_user()
    tags = create_test_tags()
    participants = create_test_participants(0)
    contest_admins = create_test_contest_admins()

    contest = Contest.objects.create(
        name=name,
        status=status,
        description=description,
        reg_start=reg_start,
        reg_end=reg_end,
        date_start=date_start,
        date_end=date_end,
        logo=logo,
        participant_cap=participant_cap,
        command_min=command_min,
        command_max=command_max,
        region=region,
        owner=owner,
    )
    contest.tags.set(tags)
    contest.participants.set(participants)
    contest.contest_admins.set(contest_admins)

    return contest

def generate_random_string(length):
    """
    Генерирует случайную строку указанной длины.
    """
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(random.choice(chars) for _ in range(length))

def create_test_user():
    """
    Создает тестового пользователя.
    """
    username = generate_random_string(8)
    email = generate_random_string(8) + '@example.com'
    password = generate_random_string(10)

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )

    return user

def create_test_tags(num_tags=3):
    """
    Создает несколько тестовых тегов.
    """
    tags = []
    for _ in range(num_tags):
        tag_name = generate_random_string(8)
        tag = Tag.objects.create(name=tag_name)
        tags.append(tag)

    return tags

def create_test_participants(num_participants=5):
    """
    Создает несколько тестовых участников.
    """
    participants = []
    for _ in range(num_participants):
        participant = create_test_user()
        participants.append(participant)

    return participants

def create_test_contest_admins(num_admins=2):
    """
    Создает несколько тестовых администраторов соревнования.
    """
    admins = []
    for _ in range(num_admins):
        admin = create_test_user()
        admins.append(admin)

    return admins

def create_test_contest_json(name_length=1):
    """
    Создает тестовый объект Contest с заполнением только обязательных полей.
    Возвращает словарь значений.
    """
    name = generate_random_string(name_length)
    status = random.choice([choice[0] for choice in Contest.Status.choices])
    description = generate_random_string(100)
    reg_start = timezone.now() - timedelta(days=random.randint(0, 30))
    reg_end = reg_start + timedelta(days=random.randint(1, 30))
    date_start = reg_end + timedelta(days=random.randint(1, 30))
    date_end = date_start + timedelta(days=random.randint(1, 30))

    contest_values = {
        'name': name,
        'status': status,
        'description': description,
        'reg_start': str(reg_start),
        'reg_end': str(reg_end),
        'date_start': str(date_start),
        'date_end': str(date_end),
    }

    return contest_values



def create_test_subscribe():
    """
    Создает тестовый объект Subscribe с заполнением случайными значениями.
    Возвращает экземпляр модели Subscribe.
    """
    name = generate_random_string(10)
    description = generate_random_string(100)
    cost = random.randint(1, 100)
    type = random.choice([choice[0] for choice in Subscribe.Type.choices])

    subscribe = Subscribe.objects.create(
        name=name,
        description=description,
        cost=cost,
        type=type
    )

    return subscribe


def create_test_award(command, task):
    """
    Создает тестовый объект Award с заполнением случайными значениями.
    Возвращает экземпляр модели Award.
    """
    name = generate_random_string(10)
    description = generate_random_string(100)
    award = generate_random_string(50)

    award = Award.objects.create(
        name=name,
        description=description,
        award=award,
        command=command,
        task=task
    )

    return award


def create_test_task(contest = None):
    """
    Создает тестовый объект Task с заполнением случайными значениями.
    Возвращает экземпляр модели Task.
    """
    task_name = generate_random_string(10)
    task_description = generate_random_string(100)

    task = Task.objects.create(
        task_name=task_name,
        task_description=task_description,
        contest = contest
    )

    return task

def create_test_command_json(name_length=10):
    """
    Создает тестовый объект Command с заполнением только обязательных полей.
    Возвращает словарь значений.
    """
    command_name = generate_random_string(name_length)
    open_to_invite = random.choice([True, False])

    command_values = {
        'command_name': command_name,
        'open_to_invite': open_to_invite,
    }

    return command_values


def create_test_command(contest, admin):
    """
    Создает тестовый объект Command с заполнением случайными значениями.
    Возвращает экземпляр модели Command.
    """
    command_name = generate_random_string(10)
    open_to_invite = random.choice([True, False])

    command = Command.objects.create(
        command_name=command_name,
        open_to_invite=open_to_invite,
        admin=admin,
        contest=contest
    )

    return command

def create_test_solution():
    """
    Создает тестовый объект Solution с заполнением случайными значениями.
    Возвращает экземпляр модели Solution.
    """
    url = generate_random_string(20)
    status = random.choice([choice[0] for choice in Solution.Status.choices])

    solution = Solution.objects.create(
        url=url,
        status=status
    )

    return solution


def create_test_solution_json(url_length=20):
    """
    Создает тестовый объект Solution с заполнением только обязательных полей.
    Возвращает словарь значений.
    """
    url = generate_random_string(url_length)
    status = random.choice([choice[0] for choice in Solution.Status.choices])

    solution_values = {
        'url': url,
        'status': status,
    }
