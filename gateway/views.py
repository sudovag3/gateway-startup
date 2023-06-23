import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

# Create your views here.

# Contest
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.generics import CreateAPIView, UpdateAPIView, ListAPIView, RetrieveAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from gateway.models import Contest, Subscribe, Command, Solution, User, Award, Task, Invite, Review
from django.db.models import Q, F, Count
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Distribution


# Test form
from django.shortcuts import render
from django.http import *

from .enums.user_contest_type import UserContestType
from .forms import TestForm, SendSolutionValidationForm, SetContestAdminValidationForm, SetParticipantValidationForm, \
    ContestForm, TaskForm, AwardForm, CommandForm
# from .bot.start import start_bot

import asyncio

from .permissions import ContestIsOwnedByMe, CommandIsOwnedByMe, SolutionIsOwnedByMe, IsSolutionIsCorrect, \
    IsNoHaveCommand, IsRequestInRegTime, SetContestAdminApprove, ValidReview, TaskOwnerOrAdminPermission, \
    AwardOwnerPermission
from .serializers import ContestAdminSerializer, ContestParticipantSerializer, ContestCreateSerializer, \
    ContestUpdateSerializer, SubscribeSerializer, CommandListSerializer, CommandUpdateSerializer, \
    CommandCreateSerializer, SolutionListSerializer, ReviewCreateSerializer, AwardSerializer, TaskSerializer, \
    AwardGetSerializer, TaskGetSerializer, InviteSerializer, UserSerializer, CommandSerializer
from .utils import type_of_user_contest


# def index(request):
#     if request.method == "POST":
#         token = request.POST.get("token")
#         output = "<h1><Бот с этим токеном: {0}</h1>" \
#                  "<h2>Успешно создан!</h2>".format(token)
#         asyncio.run(start_bot(token))
#
#         return HttpResponse(output)
#     else:
#         userform = TestForm()
#         return render(request, "../templates/index.html", {'form': userform})


@require_http_methods(["GET"])
@login_required
def contest_detail(request):
    id = request.GET.get("id", "")
    contest_qs = get_object_or_404(Contest, id=id)
    type = type_of_user_contest(request.user, id)

    if type == UserContestType.admin:
        serializer = ContestAdminSerializer(contest_qs)
    else:
        serializer = ContestParticipantSerializer(contest_qs)

    return JsonResponse(serializer.data, safe=False)


@require_http_methods(["GET"])
@login_required
def contest_detail(request):
    id = request.GET.get("id", "")
    contest_qs = get_object_or_404(Contest, id=id)
    type = type_of_user_contest(request.user, id)

    if type == UserContestType.admin:
        serializer = ContestAdminSerializer(contest_qs)
    else:
        serializer = ContestParticipantSerializer(contest_qs)

    return JsonResponse(serializer.data, safe=False)


class CreateContestAPIView(CreateAPIView):
    serializer_class = ContestCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(
            owner=self.request.user,
            status=Contest.Status.CREATED
        )
    #
    # def create(self, validated_data):
    #     validated_data['owner'] = self.request.user
    #     validated_data['status'] = Contest.Status.CREATED
    #     return super().create(validated_data)


class UpdateContestAPIView(UpdateAPIView):
    serializer_class = ContestUpdateSerializer
    permission_classes = [IsAuthenticated, ContestIsOwnedByMe]
    queryset = Contest.objects.all()


class ListSubscribeAPIView(ListAPIView):
    serializer_class = SubscribeSerializer
    permission_classes = [IsAuthenticated]
    queryset = Subscribe.objects.all()


class ListMySubscribeAPIView(ListAPIView):
    serializer_class = SubscribeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Subscribe.objects.filter(id=self.request.user.subscribe.id)


def buy_rate(request, sub_id):
    return HttpResponse("")


class ListContestAPIView(ListAPIView):
    serializer_class = ContestParticipantSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        tags = list(self.request.GET.get('tags', ""))
        status = self.request.GET.get('status', "")

        queryset = Contest.objects.all()

        if tags:
            queryset = queryset.filter(tags__name__in=tags)
        if status:
            queryset = queryset.filter(status=status)

        return queryset


class CreateCommandAPIView(CreateAPIView):
    serializer_class = CommandCreateSerializer
    permission_classes = [IsAuthenticated, IsNoHaveCommand, IsRequestInRegTime]


class UpdateCommandAPIView(UpdateAPIView):
    serializer_class = CommandUpdateSerializer
    permission_classes = [IsAuthenticated, CommandIsOwnedByMe, IsRequestInRegTime]
    queryset = Command.objects.all()


class DeleteCommandAPIView(DestroyAPIView):
    serializer_class = CommandCreateSerializer
    permission_classes = [IsAuthenticated, CommandIsOwnedByMe, IsRequestInRegTime]
    queryset = Command.objects.all()


class SearchCommandsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        contest_id = request.GET.get('contest_id')
        contest = get_object_or_404(Contest, id=contest_id)

        # get all the commands where the user is already invited
        already_invited_commands = Invite.objects.filter(invited=request.user,
                                                         status=Invite.Status.CREATED).values_list('command', flat=True)

        if contest.command_max is not None:
            commands = Command.objects.filter(
                open_to_invite=True,
                contest=contest
            ).exclude(
                id__in=already_invited_commands
            ).annotate(
                total_members=Count('participants') + 1  # count participants and add the admin
            ).filter(
                total_members__lt=contest.command_max
            )
        else:
            # If contest.command_max is not set, we simply select all teams that are open for invite.
            commands = Command.objects.filter(
                open_to_invite=True,
                contest=contest
            ).exclude(
                id__in=already_invited_commands
            )
        serializer = CommandSerializer(commands, many=True)
        return Response(serializer.data)

class LeaveFromCommandView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Leave from a command",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'command_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Command id'),
            },
        ),
        responses={
            200: "User successfully left the command",
            400: "Invalid request / Registration period is not active / User is not a participant in this command",
            403: "Only participants can leave the command",
        },
    )
    def post(self, request):
        command_id = request.data.get('command_id')

        command = get_object_or_404(Command, id=command_id)

        # Проверяем, что текущий пользователь является участником команды
        if request.user not in command.participants.all():
            return Response({"error": "Only participants can leave the command"},
                            status=status.HTTP_403_FORBIDDEN)

        # Проверяем, что регистрационный период активен
        if not command.contest.reg_start <= timezone.now() <= command.contest.reg_end:
            return Response({"error": "You can only leave the command during the registration period"},
                            status=status.HTTP_400_BAD_REQUEST)

        command.participants.remove(request.user)

        return Response({"message": "User successfully left the command"}, status=status.HTTP_200_OK)


class ListCommandAPIView(ListAPIView):
    serializer_class = CommandListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        tags = list(self.request.GET.get('tags', ""))
        contest_id = self.request.GET.get('contest_id', "")
        task_id = self.request.GET.get('task_id', "")

        queryset = Command.objects.all()

        if tags:
            queryset = queryset.filter(tags__name__in=tags)
        if contest_id:
            queryset = queryset.filter(contest_id=contest_id)
        if task_id:
            queryset = queryset.filter(task_id=task_id)

        return queryset


class GetCommandAPIView(RetrieveAPIView):
    serializer_class = CommandCreateSerializer
    permission_classes = [IsAuthenticated, CommandIsOwnedByMe]
    queryset = Command.objects.all()


class SendSolutionAPIView(APIView):
    permission_classes = (IsAuthenticated, IsSolutionIsCorrect)

    def post(self, request):
        form = SendSolutionValidationForm(request.data)
        if form.is_valid():
            solution_url = form.cleaned_data['solution_url']
            command_id = form.cleaned_data['command_id']

            command = Command.objects.filter(id=command_id).first()
            sol, created = Solution.objects.get_or_create(
                command_id=command_id,
                url=solution_url,
                task_id=command.task.id,
                status="CRE"
            )

            # Вам нужно будет добавить здесь вашу логику обработки данных формы
            return Response(SolutionListSerializer(sol).data, status=status.HTTP_200_OK)
        else:
            errors = form.errors.as_json()
            return Response({'success': False, 'errors': errors}, status=status.HTTP_400_BAD_REQUEST)


class SetContestAdminAPIView(APIView):
    permission_classes = (IsAuthenticated, SetContestAdminApprove)

    def post(self, request):
        form = SetContestAdminValidationForm(request.data)
        if form.is_valid():
            participant_id = form.cleaned_data['participant_id']
            contest_id = form.cleaned_data['contest_id']

            participant = User.objects.filter(id=participant_id)
            contest = Contest.objects.filter(id=contest_id, participants__in=participant).first()

            contest.contest_admins.set(participant)

            return Response({"success": True}, status=status.HTTP_200_OK)
        else:
            errors = form.errors.as_json()
            return Response({'success': False, 'errors': errors}, status=status.HTTP_400_BAD_REQUEST)


class SetParticipantAPIView(APIView):
    permission_classes = (IsAuthenticated, IsRequestInRegTime)

    def post(self, request):
        form = SetParticipantValidationForm(request.data)

        if form.is_valid():

            contest_id = form.cleaned_data['contest_id']

            participant = request.user
            contest = Contest.objects.filter(id=contest_id).first()

            contest.participants.add(participant)

            return Response({"success": True}, status=status.HTTP_200_OK)
        else:
            errors = form.errors.as_json()
            return Response({'success': False, 'errors': errors}, status=status.HTTP_400_BAD_REQUEST)


class CreateReviewAPIView(CreateAPIView):
    serializer_class = ReviewCreateSerializer
    permission_classes = [IsAuthenticated, ValidReview]


class ListSolutionAPIView(ListAPIView):
    serializer_class = SolutionListSerializer
    permission_classes = [IsAuthenticated, SolutionIsOwnedByMe]

    def get_queryset(self, *args, **kwargs):
        reviewed = self.request.GET.get('reviewed', "None")
        queryset = Solution.objects.all()

        if reviewed != "None":
            if reviewed == True:
                queryset = queryset.filter(command__review_to_command__reviewer_id=self.request.user.id)
            elif reviewed == False:
                queryset = queryset.filter(~Q(command__review_to_command__reviewer_id=self.request.user.id))

        return queryset


class AwardCreateView(CreateAPIView):
    queryset = Award.objects.all()
    serializer_class = AwardSerializer
    permission_classes = [IsAuthenticated, AwardOwnerPermission]


class AwardUpdateView(UpdateAPIView):
    queryset = Award.objects.all()
    serializer_class = AwardSerializer
    permission_classes = [IsAuthenticated, AwardOwnerPermission]


class AwardDeleteView(DestroyAPIView):
    queryset = Award.objects.all()
    serializer_class = AwardSerializer
    permission_classes = [IsAuthenticated, AwardOwnerPermission]


class AwardListView(ListAPIView):
    queryset = Award.objects.all()
    serializer_class = AwardGetSerializer


class TaskCreateView(CreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, TaskOwnerOrAdminPermission]


class TaskUpdateView(UpdateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, TaskOwnerOrAdminPermission]


class TaskDeleteView(DestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, TaskOwnerOrAdminPermission]


class TaskListView(ListAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskGetSerializer


class CreateInviteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        command_id = request.data.get('command')
        command = get_object_or_404(Command, id=command_id)
        contest = command.contest
        current_user = request.user
        invite_exists = Invite.objects.filter(command=command, invited=current_user,
                                              status=Invite.Status.CREATED).exists()

        other_commands = Command.objects.filter(contest=contest, participants__in=[current_user])
        if other_commands.exists():
            return Response({"error": "User is already in a command for this contest"},
                            status=status.HTTP_400_BAD_REQUEST)

        if not contest.reg_start <= timezone.now() <= contest.reg_end:
            return Response({"error": "It's not the registration period"}, status=status.HTTP_400_BAD_REQUEST)

        if not invite_exists:
            Invite.objects.create(
                command=command,
                inviter=None,
                invited=current_user,
                status=Invite.Status.CREATED
            )
            return Response({"message": "Invite successfully created"}, status=status.HTTP_201_CREATED)

        return Response({"error": "Invite could not be created"}, status=status.HTTP_400_BAD_REQUEST)


# Отправление пользователю приглашения от команды
class SendInviteView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Send an invite to a user",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'command': openapi.Schema(type=openapi.TYPE_INTEGER, description='Command id'),
                'invited': openapi.Schema(type=openapi.TYPE_INTEGER, description='Invited user id'),
            },
        ),
        responses={201: "Invite successfully sent", 400: "Invite could not be sent"},
    )
    def post(self, request):
        command_id = request.data.get('command')
        invited_id = request.data.get('invited')
        command = get_object_or_404(Command, id=command_id)
        invited = get_object_or_404(User, id=invited_id)
        contest = command.contest
        current_user = request.user
        invite_exists = Invite.objects.filter(command=command, invited=invited, status=Invite.Status.CREATED).exists()

        other_commands = Command.objects.filter(contest=contest, participants__in=[current_user])
        if other_commands.exists():
            return Response({"error": "User is already in a command for this contest"},
                            status=status.HTTP_400_BAD_REQUEST)

        if not contest.reg_start <= timezone.now() <= contest.reg_end:
            return Response({"error": "It's not the registration period"}, status=status.HTTP_400_BAD_REQUEST)

        if (current_user in command.participants.all() or current_user == command.admin) and not invite_exists:
            Invite.objects.create(
                command=command,
                inviter=current_user,
                invited=invited,
                status=Invite.Status.CREATED
            )
            return Response({"message": "Invite successfully sent"}, status=status.HTTP_201_CREATED)

        return Response({"error": "Invite could not be sent"}, status=status.HTTP_400_BAD_REQUEST)


# Просмотр списка приглашений
class InviteListView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get a list of invites for current user",
        responses={200: InviteSerializer(many=True)}
    )
    def get(self, request):
        invites = Invite.objects.filter(invited=request.user)
        serializer = InviteSerializer(invites, many=True)
        return Response(serializer.data)


class ParticipantListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, command_id):

        command = get_object_or_404(Command, id=command_id)

        # get all the users who are already invited to this command with status CREATED
        already_invited_users = list(
            Invite.objects.filter(status=Invite.Status.CREATED, command=command).values_list('invited', flat=True))

        # get all the participants and admin of this command
        command_participants_and_admin = list(command.participants.values_list('id', flat=True)) + [command.admin.id]

        # get all users who are part of a team in this contest
        contest_participant_ids = Command.objects.filter(contest=command.contest).values_list('participants__id',
                                                                                              flat=True)
        contest_admin_ids = Command.objects.filter(contest=command.contest).values_list('admin_id', flat=True)

        # get all participants of the contest who have not yet been invited to this command
        participants = User.objects.filter(Q(contests_participant=command.contest)).exclude(
            id__in=already_invited_users + command_participants_and_admin + list(contest_participant_ids) + list(
                contest_admin_ids)
        )
        serializer = UserSerializer(participants, many=True)
        return Response(serializer.data)


# Просмотр списка заявок
class ApplicationListView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get a list of applications for current user",
        responses={200: InviteSerializer(many=True)}
    )
    def get(self, request):
        applications = Invite.objects.filter(inviter=request.user)
        serializer = InviteSerializer(applications, many=True)
        return Response(serializer.data)


# Принять/отклонить запрос на вступление в команду
class AcceptDeclineApplicationView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Accept or decline an application",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'invite': openapi.Schema(type=openapi.TYPE_INTEGER, description='Invite id'),
                'accept': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Accept or decline'),
            },
        ),
        responses={200: "Invite successfully updated", 400: "Invite could not be updated"},
    )
    def post(self, request):
        invite_id = request.data.get('invite')
        accept = request.data.get('accept')
        invite = get_object_or_404(Invite, id=invite_id)
        command = invite.command

        if request.user in command.participants.all() or request.user == command.admin:
            if accept == "true":
                invite.status = Invite.Status.ACCEPTED
                command.participants.add(invite.invited)
            elif accept == "false":
                invite.status = Invite.Status.REJECTED
            invite.save()
            return Response({"message": "Invite successfully updated"}, status=status.HTTP_200_OK)

        return Response({"error": "Invite could not be updated"}, status=status.HTTP_400_BAD_REQUEST)


# Принять/отклонить приглашение в команду
class AcceptDeclineInviteView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Accept or decline an invite",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'invite': openapi.Schema(type=openapi.TYPE_INTEGER, description='Invite id'),
                'accept': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Accept or decline'),
            },
        ),
        responses={200: "Invite successfully updated", 400: "Invite could not be updated"},
    )
    def post(self, request):
        invite_id = request.data.get('invite')
        accept = request.data.get('accept')
        invite = get_object_or_404(Invite, id=invite_id)
        command = invite.command

        if request.user == invite.invited:
            if accept == 'true':
                invite.status = Invite.Status.ACCEPTED
                command.participants.add(request.user)
            elif accept == 'false':
                invite.status = Invite.Status.REJECTED
            invite.save()
            return Response({"message": "Invite successfully updated"}, status=status.HTTP_200_OK)

        return Response({"error": "Invite could not be updated"}, status=status.HTTP_400_BAD_REQUEST)


class RemoveParticipantView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Remove a participant from a command",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'command_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Command id'),
                'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='User id to be removed'),
            },
        ),
        responses={
            200: "User successfully removed from the command",
            400: "Invalid request / Registration period is not active / User is not a participant in this command",
            403: "Only command admin can remove participants",
        },
    )
    def post(self, request):
        command_id = request.data.get('command_id')
        user_id = request.data.get('user_id')

        command = get_object_or_404(Command, id=command_id)

        # Проверяем, что текущий пользователь является админом команды
        if command.admin != request.user:
            return Response({"error": "Only command admin can remove participants"},
                            status=status.HTTP_403_FORBIDDEN)

        # Проверяем, что регистрационный период активен
        if not command.contest.reg_start <= timezone.now() <= command.contest.reg_end:
            return Response({"error": "You can only remove participants during the registration period"},
                            status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, id=user_id)

        if user not in command.participants.all():
            return Response({"error": "User is not a participant in this command"},
                            status=status.HTTP_400_BAD_REQUEST)

        command.participants.remove(user)

        return Response({"message": "User successfully removed from the command"}, status=status.HTTP_200_OK)


@login_required
def home(request):
    queryset = Contest.objects.all()
    context = {
        'queryset': queryset
    }
    return render(request, 'front/index.html', context)


@login_required
def home_creator(request):
    queryset = Contest.objects.filter(Q(contest_admins__id=request.user.id) | Q(owner=request.user))
    active = queryset.filter(reg_start__lte=timezone.now(), date_end__gte=timezone.now())
    context = {
        'active': active,
        'all': queryset
    }
    return render(request, 'front/creator/home.html', context)


# TODO
@login_required
def home_participant(request):
    queryset = Contest.objects.filter(reg_start__lte=timezone.now(), date_end__gte=timezone.now())
    active = queryset.filter(participants__id=request.user.id)
    context = {
        'active': active,
        'all': queryset
    }
    return render(request, 'front/participant/home.html', context)


# TODO
@login_required
def contest_create(request):
    form = ContestForm()
    context = {
        'form': form
    }
    return render(request, 'front/creator/contest_create.html', context)


def contest_front_detail(request, contest_id):
    '''

    :param request: Это обязательный параметр в любой вьюхе, там хранятся данные запроса и пользователя
    :param contest_id: Параметр, который указывается в Query параметрах (смотри urls.py)
    :return:
    '''

    # Получаем объект из БД
    contest = get_object_or_404(Contest, id=contest_id)

    # Создаём форму для дальнейшего отображения на фронте
    contest_form = ContestForm(instance=contest)

    # Данным контекстом мы будем пользоваться на фронте
    context = {
        'user_id': request.user.id,
        'contest': contest,
        'contest_form': contest_form,
        'task_form': TaskForm(contest=contest),
        'award_form': AwardForm(contest=contest),
        'command_form': CommandForm(contest=contest),
        'participant': False,
        "tasks": Task.objects.filter(contest=contest),
        "awards": Award.objects.filter(task__contest=contest)
    }

    if request.user.is_authenticated:
        context["is_authenticated"] = True
        # Здесь мы фильтруем БД с целью понять, какое отношение пользователь имеет к выбранному хакатону
        # Участник или Владелец. В зависимости от этого возвращаем соответсвующий html
        if Contest.objects.filter(id=contest_id).filter(
                Q(contest_admins__id=request.user.id) | Q(owner=request.user)).exists():
            context["solutions"] = Solution.objects.filter(task__contest=contest)
            context["reviews"] = Review.objects.filter(command__contest=contest)

            return render(request, 'front/creator/contest_detail.html', context)

        elif Contest.objects.filter(id=contest_id).filter(participants__id=request.user.id).exists():
            context["participant"] = True
            commands_participant = Command.objects.filter(contest_id=contest_id).filter(
                Q(participants__id=request.user.id) | Q(admin=request.user.id))
            context["applications"] = Invite.objects.filter(invited=request.user, status=Invite.Status.CREATED,
                                                            command__contest_id=contest.id)
            if commands_participant.exists():
                context["command"] = commands_participant.first()
                context["command_form"] = CommandForm(instance=commands_participant.first())
                context["invites"] = Invite.objects.filter(command=commands_participant.first(),
                                                           status=Invite.Status.CREATED,
                                                           inviter=None)
                context["solutions"] = Solution.objects.filter(command=commands_participant.first())

                if commands_participant.first().admin == request.user:
                    context["command_admin"] = True


    else:
        context["is_authenticated"] = False

    return render(request, 'front/participant/contest_detail.html', context)
