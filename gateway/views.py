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

from gateway.models import Contest, Subscribe, Command, Solution, User, Award, Task, Invite
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Distribution


# Test form
from django.shortcuts import render
from django.http import *

from .enums.user_contest_type import UserContestType
from .forms import TestForm, SendSolutionValidationForm, SetContestAdminValidationForm, SetParticipantValidationForm
# from .bot.start import start_bot

import asyncio

from .permissions import ContestIsOwnedByMe, CommandIsOwnedByMe, SolutionIsOwnedByMe, IsSolutionIsCorrect, \
    IsNoHaveCommand, IsRequestInRegTime, SetContestAdminApprove, ValidReview, TaskOwnerOrAdminPermission, \
    AwardOwnerPermission
from .serializers import ContestAdminSerializer, ContestParticipantSerializer, ContestCreateSerializer, \
    ContestUpdateSerializer, SubscribeSerializer, CommandListSerializer, CommandUpdateSerializer, \
    CommandCreateSerializer, SolutionListSerializer, ReviewCreateSerializer, AwardSerializer, TaskSerializer, \
    AwardGetSerializer, TaskGetSerializer, InviteSerializer
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
        return Subscribe.objects.filter(id = self.request.user.subscribe.id)


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
    permission_classes = [IsAuthenticated, CommandIsOwnedByMe]
    queryset = Command.objects.all()


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

            command = Command.objects.filter(id = command_id).first()
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

            participant = User.objects.filter(id = participant_id)
            contest = Contest.objects.filter(id = contest_id, participants__in=participant).first()

            contest.contest_admins.set(participant)

            return Response({"success" : True}, status=status.HTTP_200_OK)
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
            contest = Contest.objects.filter(id = contest_id).first()

            contest.participants.add(participant)

            return Response({"success" : True}, status=status.HTTP_200_OK)
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
        invite_exists = Invite.objects.filter(command=command, invited=current_user, status=Invite.Status.CREATED).exists()

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
            if accept:
                invite.status = Invite.Status.ACCEPTED
                command.participants.add(invite.invited)
            else:
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
            if accept:
                invite.status = Invite.Status.ACCEPTED
                command.participants.add(request.user)
            else:
                invite.status = Invite.Status.REJECTED
            invite.save()
            return Response({"message": "Invite successfully updated"}, status=status.HTTP_200_OK)

        return Response({"error": "Invite could not be updated"}, status=status.HTTP_400_BAD_REQUEST)