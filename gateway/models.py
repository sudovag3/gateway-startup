from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings


# class CustomUserManager(BaseUserManager):
#     def create_user(self, email, first_name, last_name, password=None,
#                     ):
#         '''
#         Create a CustomUser with email, name, password and other extra fields
#         '''
#         now = timezone.now()
#         if not email:
#             raise ValueError('The email is required to create this user')
#         email = CustomUserManager.normalize_email(email)
#         cuser = self.model(email=email, first_name=first_name,
#                            last_name=last_name, is_staff=False,
#                            is_active=True, is_superuser=False,
#                            date_joined=now, last_login=now, )
#         cuser.set_password(password)
#         cuser.save(using=self._db)
#         return cuser
#
#     def create_superuser(self, email, first_name, last_name, password=None,
#                          ):
#         u = self.create_user(email, first_name, last_name, password,
#                              )
#         u.is_staff = True
#         u.is_active = True
#         u.is_superuser = True
#         u.save(using=self._db)
#
#         return u


class User(AbstractUser, PermissionsMixin):
    address = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    number = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )

    birth_date = models.DateTimeField(
        blank=True,
        null=True
    )

    class Status(models.TextChoices):
        CREATED = 'CRE', _('CREATED')
        COMPLETED = 'COM', _('COMPLETED')
        DELETED = 'DEL', _('DELETED')

    status = models.CharField(
        max_length=3,
        choices=Status.choices,
        blank=True,
        null=True
    )

    subscribe = models.ForeignKey(
        'Subscribe',
        on_delete=models.CASCADE,
        blank=True,
        null=True
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
        blank=True,
        null=True
    )

    reg_end = models.DateTimeField(
        blank=True,
        null=True
    )

    date_start = models.DateTimeField(
        blank=True,
        null=True
    )

    date_end = models.DateTimeField(
        blank=True,
        null=True
    )

    logo = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    participant_cap = models.IntegerField(
        blank=True,
        null=True
    )

    command_min = models.IntegerField(
        blank=True,
        null=True
    )

    command_max = models.IntegerField(
        blank=True,
        null=True
    )

    region = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Owner',
        on_delete=models.CASCADE,
        related_name='contests_owner'
    )

    tags = models.ManyToManyField(
        'Tag',
        null=True,
        blank=True
    )

    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name='participants',
        related_name='contests_participant',
        blank=True
        )

    contest_admins = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name='contest_admins',
        related_name='contests_admin',
        blank=True
    )


class Subscribe(models.Model):
    name = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    description = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    cost = models.IntegerField(
        blank=True,
        null=True
    )

    class Type(models.TextChoices):
        MONTHLY = 'MON', _('MONTHLY')
        YEARLY = 'YEA', _('YEARLY')
        FOREVER = 'FOR', _('FOREVER')

    type = models.CharField(
        max_length=3,
        choices=Type.choices,
        blank=True,
        null=True
    )



class Award(models.Model):

    task = models.ForeignKey(
        'Task',
        on_delete=models.PROTECT,
        related_name='task_awards',
        blank=True,
        null=True
    )

    command = models.ForeignKey(
        'Command',
        on_delete=models.PROTECT,
        related_name='command_awards',
        blank=True,
        null=True
    )

    name = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    description = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    award = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )


class Task(models.Model):

    contest = models.ForeignKey(
        'Contest',
        on_delete=models.PROTECT,
        related_name='contest_tasks',
        blank=True,
        null=True
    )

    task_name = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    task_description = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    tags = models.ManyToManyField(
        'Tag',
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )


class Command(models.Model):
    command_name = models.CharField(
        max_length=200
    )

    open_to_invite = models.BooleanField(
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    contest = models.ForeignKey(
        'Contest',
        on_delete=models.PROTECT,
        related_name='contest_commands'
    )

    task = models.ForeignKey(
        'Task',
        on_delete=models.PROTECT,
        related_name='task_commands',
        blank=True,
        null=True
    )

    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='admin_commands'
    )

    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name='Participants',
    )

    tags = models.ManyToManyField(
        'Tag'
    )


class Solution(models.Model):
    url = models.CharField(
        max_length=100
    )

    class Status(models.TextChoices):
        CREATED = 'CRE', _('CREATED')
        COMPLETED = 'REV', _('REVIEWED')
        DELETED = 'BAN', _('BANNED')

    status = models.CharField(
        max_length=3,
        choices=Status.choices
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    command = models.ForeignKey(
        'Command',
        on_delete=models.PROTECT,
        related_name='solution_to_command'
    )

    task = models.ForeignKey(
        'Task',
        on_delete=models.PROTECT,
        related_name='solution_to_task'
    )


class Invite(models.Model):
    class Status(models.TextChoices):
        CREATED = 'CRE', _('CREATED')
        COMPLETED = 'ACC', _('ACCEPTED')
        DELETED = 'REJ', _('REJECTED')

    status = models.CharField(
        max_length=3,
        choices=Status.choices
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
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

    mark = models.IntegerField(
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
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
