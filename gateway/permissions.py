from django.core.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

from gateway.models import Contest


class ContestIsOwnedByMe(BasePermission):
    message = 'You can only update contest owned or admin to you.'

    def has_object_permission(self, request, view, obj):

        if Contest.objects.filter(id = obj.id, contest_admins__id=request.user.id).exists() or Contest.objects.filter(id=obj.id, owner__id=request.user.id).exists():
            return True

        raise PermissionDenied