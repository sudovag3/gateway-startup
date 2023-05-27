from django.core.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

from gateway.forms import SendSolutionValidationForm
from gateway.github_service import GitHubService
from gateway.models import Contest, Command, Solution, Task


class ContestIsOwnedByMe(BasePermission):
    message = 'You can only update contest owned or admin to you.'

    def has_object_permission(self, request, view, obj):

        if Contest.objects.filter(id = obj.id, contest_admins__id=request.user.id).exists() or Contest.objects.filter(id=obj.id, owner__id=request.user.id).exists():
            return True

        raise PermissionDenied


class CommandIsOwnedByMe(BasePermission):
    message = 'You can only update and view command owned or admin to you.'

    def has_object_permission(self, request, view, obj):

        if Command.objects.filter(id = obj.id, admin_id=request.user.id).exists() or Command.objects.filter(id=obj.id, contest__owner__id=request.user.id).exists():
            return True

        raise PermissionDenied


class SolutionIsOwnedByMe(BasePermission):
    message = 'You can only view solution owned or admin to you.'

    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        task_id = self.request.GET.get('task_id', "")

        if Task.objects.filter(id = task_id, contest__contest_admins__in=request.user).exists() or Task.objects.filter(id = task_id, contest__owner=request.user).exists():
            return True

        raise PermissionDenied


class IsSolutionIsCorrect(BasePermission):
    message = 'You can send solution in right commit date range'

    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        form = SendSolutionValidationForm(request.POST)
        # Если форма не валидная, нужно вернуть соответсвующую ошибку
        if form.is_valid():
            solution_url = form.cleaned_data['solution_url']
            command_id = form.cleaned_data['command_id']
            is_captain = False

            #Проверяем, что пользователь - капитан
            command = Command.objects.filter(id = command_id, admin_id=request.user.id)
            if command.exists():
                is_captain = True
            git_client = GitHubService()

            is_solution_valid = git_client.has_commit_after_date(solution_url, command[0].contest.date_end)

            if is_solution_valid and is_captain:
                return True

        raise PermissionDenied


class IsNoHaveCommand(BasePermission):
    message = 'You can only once create a command'

    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        contest_id = request.data.get("contest")
        if Command.objects.filter(contest_id = contest_id, admin=request.user).exists():
            raise PermissionDenied(self.message)

        return True



