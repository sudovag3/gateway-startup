from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class User(AbstractUser):
    address = models.CharField(
        max_length=50
    )

    number = models.CharField(
        max_length=15
    )

    birth_date = models.DateTimeField(
    )

    class Status(models.TextChoices):
        CREATED = 'CRE', _('CREATED')
        COMPLETED = 'COM', _('COMPLETED')
        DELETED = 'DEL', _('DELETED')

    status = models.CharField(
        max_length=3,
        choices=Status.choices
    )

    subscribes = models.ForeignKey(
        'Subscribe',
        on_delete=models.CASCADE
    )

    contests = models.ForeignKey(
        'Contest',
        on_delete=models.CASCADE
    )

    tags = models.ForeignKey(
        'Tag',
        on_delete=models.CASCADE,
        related_name='user_to_tag'
    )


class Contest(models.Model):
    name = models.CharField(
        max_length=200
    )

    class Status(models.TextChoices):
        CREATED = 'CRE', _('CREATED')
        COMPLETED = 'COM', _('COMPLETED')
        DELETED = 'DEL', _('DELETED')

    status = models.CharField(
        max_length=3,
        choices=Status.choices
    )

    description = models.CharField(
        max_length=200
    )

    reg_start = models.DateTimeField(
    )

    reg_end = models.DateTimeField(
    )

    date_start = models.DateTimeField(
    )

    date_end = models.DateTimeField(
    )

    logo = models.CharField(
        max_length=50
    )

    participant_cap = models.IntegerField(
    )

    command_min = models.IntegerField(
    )

    command_max = models.IntegerField(
    )

    region = models.CharField(
        max_length=50
    )

    created_at = models.DateTimeField(
    )

    updated_at = models.DateTimeField(
    )

    number = models.CharField(
        max_length=15
    )

    owner = models.ForeignKey(
        'Contest',
        on_delete=models.CASCADE
    )

    tasks = models.ForeignKey(
        'Task',
        on_delete=models.CASCADE,
        related_name='contest_to_task'
    )

    commands = models.ForeignKey(
        'Command',
        on_delete=models.CASCADE,
        related_name='contest_to_command'
    )

    participants = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='User',
        on_delete=models.CASCADE,
        related_name='participants_to_user'
        )

    contest_admins = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='User',
        on_delete=models.CASCADE,
        related_name='admins_to_user'
    )

    tags = models.ForeignKey(
        'Tag',
        on_delete=models.CASCADE,
        related_name='contest_to_tag'
    )


class Subscribe(models.Model):
    name = models.CharField(
        max_length=200
    )

    description = models.CharField(
        max_length=200
    )

    cost = models.IntegerField(
    )

    class Type(models.TextChoices):
        MONTHLY = 'MON', _('MONTHLY')
        YEARLY = 'YEA', _('YEARLY')
        FOREVER = 'FOR', _('FOREVER')

    type = models.CharField(
        max_length=3,
        choices=Type.choices
    )

    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name='User',
    )


class Award(models.Model):
    task = models.CharField(
        max_length=200
    )

    commands = models.CharField(
        max_length=200
    )

    name = models.CharField(
        max_length=200
    )

    description = models.CharField(
        max_length=200
    )

    award = models.CharField(
        max_length=200
    )

    created_at = models.DateTimeField(
    )

    updated_at = models.DateTimeField(
    )


class Task(models.Model):
    contest = models.CharField(
        max_length=200
    )

    task_name = models.CharField(
        max_length=200
    )

    task_description = models.CharField(
        max_length=200
    )

    description = models.CharField(
        max_length=200
    )

    awards = models.CharField(
        max_length=200
    )

    created_at = models.DateTimeField(
    )

    updated_at = models.DateTimeField(
    )


class Command(models.Model):
    command_name = models.CharField(
        max_length=200
    )

    open_to_invite = models.BooleanField(
    )

    created_at = models.DateTimeField(
    )

    updated_at = models.DateTimeField(
    )

    contest = models.ForeignKey(
        'Contest',
        on_delete=models.CASCADE,
        related_name='command_to_contest'
    )

    invites = models.ForeignKey(
        'Invite',
        on_delete=models.CASCADE,
        related_name='command_to_invite'
    )

    participants = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='User',
        on_delete=models.CASCADE
    )

    awards = models.ForeignKey(
        'Award',
        on_delete=models.CASCADE,
    )

    solutions = models.ForeignKey(
        'Solution',
        on_delete=models.CASCADE,
        related_name='command_to_solution'
    )

    review = models.ForeignKey(
        'Review',
        on_delete=models.CASCADE,
        related_name='command_to_review'
    )

    tags = models.ForeignKey(
        'Tag',
        on_delete=models.CASCADE,
        related_name='command_to_tag'
    )


class Solution(models.Model):
    url = models.CharField(
        max_length=100
    )

    class Status(models.TextChoices):
        CREATED = 'CRE', _('CREATED')
        COMPLETED = 'COM', _('COMPLETED')
        DELETED = 'DEL', _('DELETED')

    status = models.CharField(
        max_length=3,
        choices=Status.choices
    )

    created_at = models.DateTimeField(
    )

    updated_at = models.DateTimeField(
    )

    command = models.ForeignKey(
        'Command',
        on_delete=models.CASCADE,
        related_name='solution_to_command'
    )

    task = models.ForeignKey(
        'Task',
        on_delete=models.CASCADE,
        related_name='command_to_task'
    )


class Invite(models.Model):
    class Status(models.TextChoices):
        CREATED = 'CRE', _('CREATED')
        COMPLETED = 'COM', _('COMPLETED')
        DELETED = 'DEL', _('DELETED')

    status = models.CharField(
        max_length=3,
        choices=Status.choices
    )

    created_at = models.DateTimeField(
    )

    updated_at = models.DateTimeField(
    )

    command = models.ForeignKey(
        'Command',
        on_delete=models.CASCADE,
        related_name='invite_to_command'
    )

    inviter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='User',
        on_delete=models.CASCADE,
        related_name='inviter_to_user'
    )

    invited = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='User',
        on_delete=models.CASCADE,
        related_name='invited_to_user'
    )


class Tag(models.Model):
    name = models.CharField(
        max_length=100
    )


class Review(models.Model):
    comment = models.CharField(
        max_length=100
    )

    marr = models.IntegerField(
    )

    created_at = models.DateTimeField(
    )

    updated_at = models.DateTimeField(
    )

    command = models.ForeignKey(
        'Command',
        on_delete=models.CASCADE,
        related_name='review_to_command'
    )

    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='User',
        on_delete=models.CASCADE
    )
