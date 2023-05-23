
from gateway.enums.user_contest_type import UserContestType
from gateway.models import Contest


def type_of_user_contest(user, id) -> UserContestType:
    if Contest.objects.filter(id = id, contest_admins__id=user.id).exists() or Contest.objects.filter(id= id, owner__id=user.id).exists():
        return UserContestType.admin
    elif Contest.objects.filter(id= id, participants__id=user.id).exists():
        return UserContestType.participant
    else:
        return UserContestType.guest




