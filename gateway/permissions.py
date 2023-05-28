import github
from django.core.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

from gateway.forms import SendSolutionValidationForm
from gateway.github_service import GitHubService
from gateway.models import Contest, Command, Solution, Task
from django.utils import timezone


class ContestIsOwnedByMe(BasePermission):
    message = 'You can only update contest owned or admin to you.'

    def has_object_permission(self, request, view, obj):

        if Contest.objects.filter(id = obj.id, contest_admins__id=request.user.id).exists() or Contest.objects.filter(id=obj.id, owner__id=request.user.id).exists():
            return True

        return False


class CommandIsOwnedByMe(BasePermission):
    message = 'You can only update and view command owned or admin to you.'

    def has_object_permission(self, request, view, obj):

        if Command.objects.filter(id = obj.id, admin_id=request.user.id).exists() or Command.objects.filter(id=obj.id, contest__owner__id=request.user.id).exists():
            return True

        return False


class SolutionIsOwnedByMe(BasePermission):
    message = 'You can only view solution owned or admin to you.'

    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        task_id = self.request.GET.get('task_id', "")

        if Task.objects.filter(id = task_id, contest__contest_admins__in=request.user).exists() or Task.objects.filter(id = task_id, contest__owner=request.user).exists():
            return True

        return False


class IsSolutionIsCorrect(BasePermission):
    message = 'You can send solution in right commit date range'

    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        form = SendSolutionValidationForm(request.data)
        # Если форма не валидная, нужно вернуть соответсвующую ошибку
        if form.is_valid():
            solution_url = form.cleaned_data['solution_url']
            command_id = form.cleaned_data['command_id']

            if not Command.objects.filter(id = command_id).exists():
                self.message = "Command does not exist"
                return False

            is_captain = False

            #Проверяем, что пользователь - капитан
            command = Command.objects.filter(id = command_id, admin_id=request.user.id)
            if command.exists():
                is_captain = True
            git_client = GitHubService()
            try:
                is_solution_not_valid = git_client.has_commit_after_date(solution_url, command[0].contest.date_end)
            except github.GithubException as e:
                self.message = f"You must send a correct github repository url - {e.data}"
                return False

            if not is_solution_not_valid and is_captain:
                return True
        else:
            self.message = form.errors

        return False


class IsNoHaveCommand(BasePermission):
    message = 'You can only once create a command'

    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        contest_id = request.data.get("contest")
        if Command.objects.filter(contest_id = contest_id, admin=request.user).exists():
            return False

        return True


class IsRequestInRegTime(BasePermission):
    message = 'The request should be made between reg_start and reg_end of the contest'

    def has_permission(self, request, view):
        contest_id = request.data.get("contest")
        contest = Contest.objects.filter(id=contest_id).first()
        if not contest:
            return False

        if contest.reg_start <= timezone.now() <= contest.reg_end:
            return True




class IsRequestInContestTime(BasePermission):
    message = 'The request should be made between date_start and date_end of the contest'

    def has_permission(self, request, view):
        contest_id = request.data.get("contest")
        contest = Contest.objects.filter(id=contest_id).first()
        if not contest:
            raise PermissionDenied('Contest not found')

        if contest.date_start <= timezone.now() <= contest.date_end:
            return True

        raise PermissionDenied(self.message)




