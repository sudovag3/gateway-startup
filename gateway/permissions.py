from django.core.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

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

        return True

    def has_object_permission(self, request, view, obj):

        if Solution.objects.filter(id = obj.id, admin_id=request.user.id).exists() or Command.objects.filter(id=obj.id, contest__owner__id=request.user.id).exists():
            return True

        raise PermissionDenied
